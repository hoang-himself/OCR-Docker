import re
import inspect
import pyproj

#############################################
##										   ##
#	Get potential coordinates from file 	#
##										   ##
#############################################

"""
Algorithm: Getting potential coordinates from content by grading method
Return-value: array contains potential coordinates

Approach: For each line we read from file, assign points to it by number_grading,
which explain below.

`number_grading`:
Each line, init point = 0, every time we see a number character in line, increase
points by 1.

The following condition must be satisfied if a line is potential coordinate
- The point is not 0 after we go through all characters
- There is a dot(character '.') inside string
- The difference between length of string and points <= 3

If above condition are met, add line to array.
"""


def number_grading(string, raw_coordinates):
    string = re.sub("\s+", "", string)
    string = re.sub("\\n\\x0c", "", string)
    points = 0
    for char in string:
        if char.isdigit():
            points += 1

    if len(string) - points <= 3 and points != 0 and '.' in string:
        raw_coordinates.append(string)


def filter_potential_coordinates(input_text):
    raw_coordinates = []
    for text in input_text:
        number_grading(text, raw_coordinates)

    return raw_coordinates

#########################
#						#
# Remove non-coordinate #
#						#
#########################

# There are some wrong coordinates like: 4.0, 12.25 -> remove these wrong coordinates
# Keep the coordinate whose length >= 9


def rm_non_coordinate(raw_coordinates):
    _potentials = []
    for coordinate in raw_coordinates:
        if len(coordinate) >= 9:
            _potentials.append(coordinate)

    return _potentials

#########################################
#										#
#	Convert string coordinate to float 	#
#										#
#########################################


def replaceChar(special_coordinate):
    char2number = {
        'b': '1',
        't': '1',
        '$': '5',
        'S': '5',
        '§': '5',
        '%': '',
        ']': '',
        '¢': ''
    }
    good_coordinate = []
    for char in special_coordinate:
        if char in char2number:
            good_coordinate.append(char2number[char])
        else:
            good_coordinate.append(char)

    return_str = "".join(good_coordinate)
    return return_str

# there is some coordinates which has two dots in the string -> fallacy of OCR
# However, removing the first dots(leaving the last dot) could give us the coordinate.


def remove_multi_dots(fail_coordinate):
    number_dots = 0
    one_dot_coordinate = []
    for char in fail_coordinate:
        if char == '.':
            number_dots += 1

    # only have 1 dot
    if number_dots == 1:
        return fail_coordinate
    else:
        for char in fail_coordinate:
            if char == '.' and number_dots != 1:
                number_dots -= 1
            else:
                one_dot_coordinate.append(char)

        return "".join(one_dot_coordinate)


def convert_coordinate(str_coordinate):
    try:
        return float(str_coordinate)
    except:
        one_dot_coordinate = remove_multi_dots(str_coordinate)
        try:
            return float(one_dot_coordinate)
        except:
            potential_str = replaceChar(one_dot_coordinate)
            try:
                return float(potential_str)
            except:
                print(f"Error: Couldn't convert {potential_str}")
                return None

#########################
#						#
#	Group coordinate 	#
#						#
#########################


"""
Algorithm: Grouping coordinates based on 2 first digits.

Return: a hash table in which keys are two first digit,values are array of
coordinates with same first two digits
"""


def group(coordinates, groups):
    for coordinate in coordinates:
        coordinate_str = str(coordinate)
        # get 2 first digit
        two_digits = int(coordinate_str[0:2:1])
        if two_digits not in groups:
            groups[two_digits] = []

        groups[two_digits].append(coordinate)


def vn2k_to_wgs84(coordinate, crs):
    """
    Đây là hàm chuyển đổi cặp toạ độ x, y theo vn2k sang kinh độ , vĩ độ theo khung toạ độ của Google Map
    Công thức này được cung cấp bởi thư viện pyproj


    Input:

        - ( x, y ) : TUPLE chứa cặp toạ độ x và y theo đơn vị float
        - crs : INT - id (mã) vùng chứa cặp toạ độ x, y theo toạ độ Google

    Output:

        - (longitude, latitude): TUPLE chứa cặp kinh độ - vĩ độ theo toạ độ Google Map
    """
    new_coordinate = pyproj.Transformer.from_crs(
        crs_from=crs, crs_to=4326, always_xy=True).transform(coordinate[1], coordinate[0])

    return new_coordinate

#############################
#							#
#	Determine X, Y groups 	#
#							#
#############################


"""
Based on bias of picture, X coordinates usually begin with '1'
If there are many potential candidate for X, choose the groups that has most
element
"""


def text2Coordinate(input_text):
    coordinates = {}
    raw_coordinates = filter_potential_coordinates(input_text)

    if len(raw_coordinates) == 0:
        return None

    potential_coordinates = rm_non_coordinate(raw_coordinates)

    real_coordinates = []
    for potential in potential_coordinates:
        coordinate = convert_coordinate(potential)
        if coordinate is not None:
            real_coordinates.append(coordinate)

    groups = {}
    group(real_coordinates, groups)

    max_len = 0
    for key in groups.keys():
        if key // 10 == 1:
            if len(groups[key]) > max_len:
                coordinates['X'] = groups[key]
                max_len = len(groups[key])
        else:
            coordinates['Y'] = groups[key]

    return coordinates


def text_to_coordinate(input_text, crs: int):
    coordinates = text2Coordinate(input_text)
    lat, lon = vn2k_to_wgs84((coordinates['X'][0], coordinates['Y'][0]), crs)
    return lat, lon
