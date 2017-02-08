var CANVAS_HEIGHT = 600;
var CANVAS_WIDTH = 600;
var CANVAS_PADDING = 100; // padding on all sides of canvas

function getCursorPosition(canvas, event) {
  var rect = canvas.getBoundingClientRect();
  var x = event.clientX - rect.left;
  var y = event.clientY - rect.top;
  return [x, y];
}

function getPolarCoordinates(canvas, x, y) {
  u = x - 0.5 * canvas.width;
  z = 0.5 * canvas.height - y;
  var theta;
  if (u>0 && z>0) {
    theta = Math.atan(u / z) * 180 / Math.PI;
  } else if (u>0 && z<0) {
    theta = Math.atan(u / z) * 180 / Math.PI + 180;
  } else if (u<0 && z<0) {
    theta = Math.atan(u / z) * 180 / Math.PI + 180;
  } else {
    theta = Math.atan(u / z) * 180 / Math.PI + 360;
  }
  r = Math.sqrt(u * u + z * z) / ((canvas.width - CANVAS_PADDING) / 2);
  // console.log("u: " + u + " z: " + z + " theta: " + theta + " r: " + r);

  return [theta, r];
}

function getCartesian(canvas, theta, r) {
  var x = CANVAS_WIDTH / 2 * (1 + r * Math.sin(theta / 180 * Math.PI));
  x -= CANVAS_PADDING / 2 * r * Math.sin(theta / 180 * Math.PI);
  var y = CANVAS_HEIGHT / 2 * (1 - r * Math.cos(theta / 180 * Math.PI));
  y += CANVAS_PADDING / 2 * r * Math.cos(theta / 180 * Math.PI);
  // console.log("theta:" + theta + "sin:" + Math.sin(theta) + " cos:" + Math.cos(theta));
  return [x, y];
}

function drawImage(canvas, imageObj) {
  context = canvas.getContext("2d");
  context.drawImage(imageObj, CANVAS_PADDING / 2, CANVAS_PADDING / 2, canvas.height - CANVAS_PADDING, canvas.height - CANVAS_PADDING);
}

function drawCircle(canvas, theta, r) {
  // clamp it to the circle
  if (r > 1) r = 1;

  // convert back to x, y
  [x, y] = getCartesian(canvas, theta, r);
  ctx = canvas.getContext("2d");
  ctx.beginPath();
  ctx.arc(x, y, 10, 0, 2*Math.PI);
  ctx.lineWidth = 5;
  ctx.stroke();
}

function drawBoth(canvas, e, imageObj) {
  [x, y] = getCursorPosition(canvas, e);

  context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
  drawImage(canvas, imageObj);

  [theta, r] = getPolarCoordinates(canvas, x, y);
  drawCircle(canvas, theta, r);
}

// Returns a function, that, when invoked, will only be triggered at most once
// during a given window of time. Normally, the throttled function will run
// as much as it can, without ever going more than once per `wait` duration;
// but if you'd like to disable the execution on the leading edge, pass
// `{leading: false}`. To disable execution on the trailing edge, ditto.
function throttle(func, wait, options) {
  // http://stackoverflow.com/questions/27078285/simple-throttle-in-js
  var context, args, result;
  var timeout = null;
  var previous = 0;
  if (!options) options = {};
  var later = function() {
    previous = options.leading === false ? 0 : Date.now();
    timeout = null;
    result = func.apply(context, args);
    if (!timeout) context = args = null;
  };
  return function() {
    var now = Date.now();
    if (!previous && options.leading === false) previous = now;
    var remaining = wait - (now - previous);
    context = this;
    args = arguments;
    if (remaining <= 0 || remaining > wait) {
      if (timeout) {
        clearTimeout(timeout);
        timeout = null;
      }
      previous = now;
      result = func.apply(context, args);
      if (!timeout) context = args = null;
    } else if (!timeout && options.trailing !== false) {
      timeout = setTimeout(later, remaining);
    }
    return result;
  };
}

$(function() {
  var canvas = document.getElementById('colorpicker');
  var context = canvas.getContext('2d');
  var imageObj = new Image();
  // set up the canvas
  canvas.width = CANVAS_WIDTH;
  canvas.height = CANVAS_HEIGHT;

  imageObj.onload = function() {drawImage(canvas, imageObj);};
  imageObj.src = '/static/color-wheel-fix.jpg';

  var socket = io.connect('http://' + document.domain + ':5001');
  var cycle = {
    'module':'couch',
    'command':'cycle',
    'data': {
      'period_min':1,
      'saturation':1,
      'intensity':1
    }
  };

  var blink = {
    'module':'couch',
    'command':'blink',
    'data': {
      'freq_hz':1
    }
  };

  var pulse = {
    'module':'couch',
    'command':'pulse',
    'data': {
      'freq_hz':1
    }
  };

  var hsi = {
    // 'module':'couch',
    'command':'hsi',
    'data': {
      'hue': 90,
      'saturation':1,
      'intensity':1
    }
  };

  canvas.addEventListener('click', function(e){
    drawBoth(canvas, e, imageObj);
  }, false);

  var mouseMove = function(e) {
    [x, y] = getCursorPosition(canvas, e);

    context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);
    drawImage(canvas, imageObj);

    [theta, r] = getPolarCoordinates(canvas, x, y);
    drawCircle(canvas, theta, r);
    sendHSI(theta, r);
  };

  var sendHSI = throttle(function() {
    var hsi = {
      // 'module':'couch',
      'command':'hsi',
      'data': {
        'hue': theta,
        'saturation': r,
        'intensity':1
      }
    };
    socket.emit('nanio-event', hsi);
  }, 500);

  canvas.addEventListener('mousedown', function(e){
    canvas.addEventListener('mousemove', mouseMove);
    mouseMove(e);
  });

  canvas.addEventListener('mouseup', function(e){
    canvas.removeEventListener('mousemove', mouseMove);
  });

  socket.on('message', function(m){
    console.log(m);
  });


});
