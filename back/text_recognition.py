# Import needed library
import sys
import os
import time

import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
from torch.autograd import Variable

from PIL import Image

import cv2
from skimage import io
import numpy as np
import craft_utils
import imgproc

from craft import CRAFT
# OrderedDict: dictionary subclass that remembers the order that keys were first inserted
from collections import OrderedDict
import copy

import pytesseract

# Define CRAFT function
UNCLASSIFIED = -2
NOISE = -1


def copyStateDict(state_dict):
    if list(state_dict.keys())[0].startswith("module"):
        start_idx = 1
    else:
        start_idx = 0
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = ".".join(k.split(".")[start_idx:])
        new_state_dict[name] = v
    return new_state_dict


def str2bool(v):
    return v.lower() in ("yes", "y", "true", "t", "1")


def test_net(net, canvas_size, mag_ratio, image, text_threshold, link_threshold, low_text, cuda, poly, refine_net=None):
    t0 = time.time()
    # resize
    img_resized, target_ratio, size_heatmap = imgproc.resize_aspect_ratio(
        image, canvas_size, interpolation=cv2.INTER_LINEAR, mag_ratio=mag_ratio)
    ratio_h = ratio_w = 1 / target_ratio

    # preprocessing
    x = imgproc.normalizeMeanVariance(img_resized)
    x = torch.from_numpy(x).permute(2, 0, 1)    # [h, w, c] to [c, h, w]
    x = Variable(x.unsqueeze(0))                # [c, h, w] to [b, c, h, w]
    # print("X: ",x)

    if cuda:
        x = x.cuda()

    # forward pass
    with torch.no_grad():
        y, feature = net(x)

    # make score and link map
    score_text = y[0, :, :, 0].cpu().data.numpy()
    score_link = y[0, :, :, 1].cpu().data.numpy()
    # print("Score_text: ", score_text)
    # print("Score_link: ", score_link)

    # refine link
    if refine_net is not None:
        with torch.no_grad():
            y_refiner = refine_net(y, feature)
        score_link = y_refiner[0, :, :, 0].cpu().data.numpy()
    t0 = time.time() - t0
    t1 = time.time()

    # Post-processing
    boxes, polys = craft_utils.getDetBoxes(
        score_text, score_link, text_threshold, link_threshold, low_text, poly)

    # coordinate adjustment
    boxes = craft_utils.adjustResultCoordinates(boxes, ratio_w, ratio_h)
    polys = craft_utils.adjustResultCoordinates(polys, ratio_w, ratio_h)
    for k in range(len(polys)):
        if polys[k] is None:
            polys[k] = boxes[k]
    t1 = time.time() - t1

    # render results (optional)
    render_img = score_text.copy()
    render_img = np.hstack((render_img, score_link))
    ret_score_text = imgproc.cvt2HeatmapImg(render_img)
    # print("Render image: ", render_img)
    # plt.imshow(ret_score_text)
    # print("Bounding Box: ", polys)

    # if show_time : print("\ninfer/postproc time : {:.3f}/{:.3f}".format(t0, t1))

    return boxes, polys, ret_score_text


class Point:
    '''
    Each point have 2 main values: coordinate(lat, long) and cluster_id
    '''

    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.cluster_id = UNCLASSIFIED

    def __repr__(self):
        return '(x:{}, y:{}, id:{}, cluster:{})' \
            .format(self.x, self.y, self.id, self.cluster_id)

# In G-DBScan we use eclipse instead of circle to cluster (because we mainly use for horizontal text image --> elip is more useful)


def n_pred(p1, p2):
    # return (p1.x - p2.x)**2/160000 + (p1.y - p2.y)**2/2500 <= 1
    #print(p1.x -p2.x)
    #print(p1.y -p2.y)
    # return (p1.x - p2.x)**2/50000 + (p1.y - p2.y)**2/1500 <= 1
    # return (p1.x - p2.x)**2/20000 + (p1.y - p2.y)**2/1300 <= 1
    # return (p1.x - p2.x)**2/2000 + (p1.y - p2.y)**2/130 <= 1
    return (p1.x - p2.x)**2/500 + (p1.y - p2.y)**2/70 <= 1
    # return (p1.x - p2.x)**2/3500 + (p1.y - p2.y)**2/150 <= 1
    # return (p1.x - p2.x)**2/7000 + (p1.y - p2.y)**2/1300 <= 1
    # return (p1.x - p2.x)**2/8000 + (p1.y - p2.y)**2/300 <= 1
    # return (p1.x - p2.x)**2/17000 + (p1.y - p2.y)**2/300 <= 1
    # return (p1.x - p2.x)**2/13000 + (p1.y - p2.y)**2/250 <= 1
    # return (p1.x - p2.x)**2/15000 + (p1.y - p2.y)**2/180 <= 1


def w_card(points):
    return len(points)


def GDBSCAN(points, n_pred, min_card, w_card):
    points = copy.deepcopy(points)
    cluster_id = 0
    for point in points:
        if point.cluster_id == UNCLASSIFIED:
            if _expand_cluster(points, point, cluster_id, n_pred, min_card,
                               w_card):
                cluster_id = cluster_id + 1
    clusters = {}
    for point in points:
        key = point.cluster_id
        if key in clusters:
            clusters[key].append(point)
        else:
            clusters[key] = [point]
    return list(clusters.values())


def _expand_cluster(points, point, cluster_id, n_pred, min_card, w_card):
    if not _in_selection(w_card, point):
        points.change_cluster_id(point, UNCLASSIFIED)
        return False

    seeds = points.neighborhood(point, n_pred)
    if not _core_point(w_card, min_card, seeds):
        points.change_cluster_id(point, NOISE)
        return False

    points.change_cluster_ids(seeds, cluster_id)
    seeds.remove(point)

    while len(seeds) > 0:
        current_point = seeds[0]
        result = points.neighborhood(current_point, n_pred)
        if w_card(result) >= min_card:
            for p in result:
                if w_card([p]) > 0 and p.cluster_id in [UNCLASSIFIED, NOISE]:
                    if p.cluster_id == UNCLASSIFIED:
                        seeds.append(p)
                    points.change_cluster_id(p, cluster_id)
        seeds.remove(current_point)
    return True


def _in_selection(w_card, point):
    return w_card([point]) > 0


def _core_point(w_card, min_card, points):
    return w_card(points) >= min_card


class Points:
    'Contain list of Point'

    def __init__(self, points):
        self.points = points

    def __iter__(self):
        for point in self.points:
            yield point

    def __repr__(self):
        return str(self.points)

    def get(self, index):
        return self.points[index]

    def neighborhood(self, point, n_pred):
        return list(filter(lambda x: n_pred(point, x), self.points))

    def change_cluster_ids(self, points, value):
        for point in points:
            self.change_cluster_id(point, value)

    def change_cluster_id(self, point, value):
        index = (self.points).index(point)
        self.points[index].cluster_id = value

    def labels(self):
        return set(map(lambda x: x.cluster_id, self.points))


def applyCraft(image_file):
    # Initialize CRAFT parameters
    text_threshold = 0.7
    low_text = 0.4
    link_threshold = 0.4
    cuda = False
    canvas_size = 1280
    mag_ratio = 1.5
    # if text image present curve --> poly=true
    poly = False
    refine = False
    show_time = False
    refine_net = None
    trained_model_path = '/app/CRAFT/craft_mlt_25k.pth'

    net = CRAFT()
    net.load_state_dict(copyStateDict(torch.load(
        trained_model_path, map_location='cpu')))
    net.eval()

    image = imgproc.loadImage(image_file)

    poly = False
    refine = False
    show_time = False
    refine_net = None
    bboxes, polys, score_text = test_net(
        net, canvas_size, mag_ratio, image, text_threshold, link_threshold, low_text, cuda, poly, refine_net)

    # Compute coordinate of central point in each bounding box returned by CRAFT
    # Purpose: easier for us to make cluster in G-DBScan step
    poly_indexes = {}
    central_poly_indexes = []
    for i in range(len(polys)):
        poly_indexes[i] = polys[i]
        x_central = (polys[i][0][0] + polys[i][1][0] +
                     polys[i][2][0] + polys[i][3][0])/4
        y_central = (polys[i][0][1] + polys[i][1][1] +
                     polys[i][2][1] + polys[i][3][1])/4
        central_poly_indexes.append({i: [int(x_central), int(y_central)]})

    # for i in central_poly_indexes:
    #   print(i)

    # For each of these cordinates convert them to new Point instances
    X = []

    for idx, x in enumerate(central_poly_indexes):
        point = Point(x[idx][0], x[idx][1], idx)
        X.append(point)

    # Cluster these central points
    clustered = GDBSCAN(Points(X), n_pred, 1, w_card)

    cluster_values = []
    for cluster in clustered:
        sort_cluster = sorted(cluster, key=lambda elem: (elem.x, elem.y))
        max_point_id = sort_cluster[len(sort_cluster) - 1].id
        min_point_id = sort_cluster[0].id
        max_rectangle = sorted(
            poly_indexes[max_point_id], key=lambda elem: (elem[0], elem[1]))
        min_rectangle = sorted(
            poly_indexes[min_point_id], key=lambda elem: (elem[0], elem[1]))

        right_above_max_vertex = max_rectangle[len(max_rectangle) - 1]
        right_below_max_vertex = max_rectangle[len(max_rectangle) - 2]
        left_above_min_vertex = min_rectangle[0]
        left_below_min_vertex = min_rectangle[1]

        if (int(min_rectangle[0][1]) > int(min_rectangle[1][1])):
            left_above_min_vertex = min_rectangle[1]
            left_below_min_vertex = min_rectangle[0]
        if (int(max_rectangle[len(max_rectangle) - 1][1]) < int(max_rectangle[len(max_rectangle) - 2][1])):
            right_above_max_vertex = max_rectangle[len(max_rectangle) - 2]
            right_below_max_vertex = max_rectangle[len(max_rectangle) - 1]

        cluster_values.append([left_above_min_vertex, left_below_min_vertex,
                               right_above_max_vertex, right_below_max_vertex])

    image = imgproc.loadImage(image_file)
    img = np.array(image[:, :, ::-1])
    img = img.astype('uint8')
    ocr_res = []
    for i, box in enumerate(cluster_values):
        poly = np.array(box).astype(np.int32).reshape((-1))
        poly = poly.reshape(-1, 2)

        rect = cv2.boundingRect(poly)
        x, y, w, h = rect
        cropped = img[y:y+h, x:x+w].copy()

        # Preprocess cropped segment
        cropped = cv2.resize(cropped, None, fx=5, fy=5,
                             interpolation=cv2.INTER_LINEAR)
        cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        cropped = cv2.GaussianBlur(cropped, (3, 3), 0)
        cropped = cv2.bilateralFilter(cropped, 5, 25, 25)
        cropped = cv2.dilate(cropped, None, iterations=1)
        cropped = cv2.threshold(
            cropped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        #cropped = cv2.threshold(cropped, 90, 255, cv2.THRESH_BINARY)[1]
        #cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)

        ocr_res.append(pytesseract.image_to_string(cropped, lang='eng'))

    return ocr_res


def text_recognition(image_file):
    input_text = applyCraft(image_file)
    return input_text
