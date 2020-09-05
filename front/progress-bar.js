var percentage = 1;
var switcher = 0;
var speed = 0.1;
var able_draw_map = 0;
function setup() {
  createCanvas(200, 200).parent("p5js");
  background(255);
  percentage = 0;
  switcher = 0;
  speed = 0;
  able_draw_map = 0;
}

function draw() {
  background(255);
  drawProgress(percentage);
  if (round(percentage) < 100 && percentage != 0) {
    percentage += speed;
    speed = whichSpeed();
  } else if (percentage != 0) {
    background(255);
    document.querySelector("#p5js").style.display = 'none';
    document.querySelector("#map").style.display = 'block';
  } else {
    background(255);
  }
}

function drawProgress(stop) {
  translate(width/2, height/2);
  rotate(-PI/2.0);
  noFill();
  strokeWeight(4);
  arc(0,0,150,150,0,2*PI * stop / 100);
  
  fill(0,0,0);
  rotate(PI/2);
  textSize(18);
  textAlign(CENTER);
  text(round(stop)+"%",0,0);
}

function whichSpeed() {
  if (switcher == 0) {
    return 0;
  } else if (switcher == 1) {
    return 0.1;
  } else if (switcher == 2) {
    return 1;
  }
}