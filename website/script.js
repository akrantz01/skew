var $win = $(window),
  w = 0,
  h = 0,
  rgb = [],
  getWidth = function() {
    w = $win.width();
    h = $win.height();
  };


var average = function(a, b) {
  return [0.5 * (a[0] + b[0]), 0.5 * (a[1] + b[1]), 0.5 * (a[1] + b[1])];
}

var center = [152, 99, 146]; // purple
var topMiddle = [191, 124, 178]; // white-purple
var leftMiddle = [66, 133, 244]; // red
var rightMiddle = [234, 67, 53]; // blue
var bottomMiddle = [88, 57, 84]; // black-purple


var topLeft = average(leftMiddle, topMiddle);
var topRight = average(topMiddle, rightMiddle);
var bottomLeft = average(leftMiddle, bottomMiddle);
var bottomRight = average(bottomMiddle, rightMiddle);


var interpolate2D = function(x00, x01, x10, x11, x, y) {
  return x00 * (1 - x) * (1 - y) + x10 * x * (1 - y) + x01 * (1 - x) * y + x11 * x * y;
}

var interpolateArray = function(x00, x01, x10, x11, x, y) {
  var result = [0, 0, 0];
  for (var i = 0; i < 3; ++i) {
    result[i] = Math.floor(interpolate2D(x00[i], x01[i], x10[i], x11[i], x, y));
  }
  return result;
}


$win.resize(getWidth).mousemove(function(e) {
  var positionX = e.pageX / w;
  var positionY = e.pageY / h;
  var x00, x01, x11, x10;

  if (positionX > 0.5 && positionY > 0.5) {
    x00 = center;
    x01 = bottomMiddle;
    x10 = rightMiddle;
    x11 = bottomRight;
    positionX = 2.0 * (positionX - 0.5); // scale position back to [0, 1]
    positionY = 2.0 * (positionY - 0.5);
  } else if (positionX > 0.5 && positionY <= 0.5) {
    x00 = topMiddle;
    x01 = center;
    x10 = topRight;
    x11 = rightMiddle;
    positionX = 2.0 * (positionX - 0.5);
    positionY = 2.0 * (positionY);
  } else if (positionX <= 0.5 && positionY <= 0.5) {
    x00 = topLeft;
    x01 = leftMiddle;
    x10 = topMiddle;
    x11 = center;
    positionX = 2.0 * (positionX);
    positionY = 2.0 * (positionY);
  } else if (positionX <= 0.5 && positionY > 0.5) {
    x00 = leftMiddle;
    x01 = bottomLeft;
    x10 = center;
    x11 = bottomMiddle;
    positionX = 2.0 * (positionX);
    positionY = 2.0 * (positionY - 0.5);
  } else {
    // can't happen
  }

  rgb = interpolateArray(x00, x01, x10, x11, positionX, positionY);

  $('#colorChange').css('color', 'rgb(' + rgb.join(',') + ')');
}).resize();
