var ws;
var titlesjumbo = document.getElementById("titlesjumbo");
var currentTitle = document.getElementById("current");
var nextTitle = document.getElementById("next");
// media buttons
var backwardbtn = document.getElementById("backward-btn");
var playbtn = document.getElementById("play-btn");
var pausebtn = document.getElementById("pause-btn");
var stopbtn = document.getElementById("stop-btn");
var forwardbtn = document.getElementById("forward-btn");
// status
var statusbadges = document.getElementsByClassName("statusbadge");
// scroll animation
var banners = document.getElementsByClassName("banner-scroll");

var wsurl = document.URL.replace(/^http/g, 'ws').replace(/\/$/g, '') + wsurl;
console.log("Websocket URL is " + wsurl);

document.onload = connect(wsurl);
window.onload = preloadImages();
window.onbeforeunload = function() {
  ws = undefined; // don't reconnect while reloading page
};


function connect(wsurl) {
  if (ws == undefined || ws.readyState == ws.CLOSED) {
    ws = new WebSocket(wsurl);
    ws.onopen = onopen;
    ws.onmessage = onmessage;
    ws.onclose = onclose;
    ws.onerror = function (error) {
      console.log('WebSocket Error ' + error);
      update_status();
    };
    console.log("Connected");
    update_status();
  }
}

function onopen() {
  update_status();
};

function onmessage(evt) {
  var message = JSON.parse(evt.data);
  console.log(message)
  if (message.current != undefined) {
    currentTitle.innerHTML = message.current;
  }
  if (message.next != undefined) {
    nextTitle.innerHTML = message.next;
  }
  if (message.status != undefined) {
    switch (message.status) {
      case 'playing':
        playbtn.style.display = "none";
        pausebtn.style.display = "inline-block";
        stopbtn.disabled = false;
        titlesjumbo.style.backgroundImage = "url(" + titlesjumbo.dataset.bckgrndPlay + ")";
        break;
      case 'paused':
        playbtn.style.display = "inline-block";
        pausebtn.style.display = "none";
        stopbtn.disabled = false;
        titlesjumbo.style.backgroundImage = "url(" + titlesjumbo.dataset.bckgrndPause + ")";
        break;
      case 'stopped':
        playbtn.style.display = "inline-block";
        pausebtn.style.display = "none";
        stopbtn.disabled = true;
        titlesjumbo.style.backgroundImage = "url(" + titlesjumbo.dataset.bckgrndStop + ")";
        break;
      default:
        console.log("Invalid playback status " + message.status)
    }
  }
};

function onclose() {
  if (ws != undefined && ws.readyState == ws.CLOSED) {
    console.log("Disconnected");
    update_status();
    setTimeout(connect(wsurl), 1000);
  }
}

function send(action) {
  var message = {
    "action": action,
  }
  ws.send(JSON.stringify(message));
  console.log(action)
}

function backward() {
  send("backward");
}

function play() {
  send("play");
}

function pause() {
  send("pause");
}

function forward() {
  send("forward");
}

function stop() {
  send("stop");
}

function update_status() {
  for (var i = 0, l = statusbadges.length; i < l; i++) {
    if (ws.readyState == ws.OPEN) {
      statusbadges[i].className = "statusbadge statusbadge-ok";
    } else if (ws.readyState == ws.CONNECTING || ws.readyState == ws.CLOSING) {
      statusbadges[i].className = "statusbadge statusbadge-progress";
    } else {
      statusbadges[i].className = "statusbadge statusbadge-problem";
    }
  }
}

// preload titlesjumbo background images:
function preloadImages() {
  img = new Image();
  img.src = titlesjumbo.dataset.bckgrndPlay;
  img.src = titlesjumbo.dataset.bckgrndPause;
  img.src = titlesjumbo.dataset.bckgrndStop;
}

// scroll animations
// TODO
