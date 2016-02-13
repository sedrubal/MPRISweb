/* main functions and websocket handling */

var ws;
var playstatuslayer = document.getElementById("playstatuslayer");
var artimagelayer = document.getElementById("artimagelayer")
var currentTitle = document.getElementById("current");
var nextTitle = document.getElementById("next");
var nextTitleHeading = document.getElementById("next-heading");
var trackDetails = document.getElementById("track-details");
var artimages = document.getElementsByClassName("artimage");
// media buttons
var mediabtndiv = document.getElementById("mediabtns");
var backwardbtn = document.getElementById("backward-btn");
var playbtn = document.getElementById("play-btn");
var pausebtn = document.getElementById("pause-btn");
var stopbtn = document.getElementById("stop-btn");
var forwardbtn = document.getElementById("forward-btn");
// status
var statusbadges = document.getElementsByClassName("statusbadge");
// scroll animation
var banners = document.getElementsByClassName("banner-scroll");

var wsurl = document.URL.replace(/^http/g, 'ws').split('#')[0].split('?')[0].replace(/\/$/g, '') + wsurl;
console.log("Websocket URL is " + wsurl);

window.onload = function onLoad() {
  connect(wsurl);
  onWindowResize();
  preloadStatusImages();
};
window.onbeforeunload = function() {
  ws = undefined; // don't reconnect while reloading page
};
window.onresize = onWindowResize;


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
  if (message.titles.current != undefined) {
    currentTitle.innerHTML = message.titles.current;
  }
  if (message.titles.next != undefined) {
    nextTitle.innerHTML = message.titles.next;
    nextTitleHeading.classList.remove("hide");
  } else {
    nextTitleHeading.classList.add("hide");
  }
  if (message.player.canControl != undefined && !message.player.canControl) {
    mediabtndiv.classList.add("hide");
  } else {
    mediabtndiv.classList.remove("hide");
  }
  var showBack = true, showFor = true, showPlay = true, showPause = true, enableStop = true;
  if (message.status != undefined) {
    switch (message.status) {
      case 'playing':
        showPlay &= false;
        showPause &= true;
        enableStop &= true;
        playstatuslayer.style.backgroundImage = "url(" + playstatuslayer.dataset.bckgrndPlay + ")";
        break;
      case 'paused':
        showPlay &= true;
        showPause &= false;
        enableStop &= true;
        playstatuslayer.style.backgroundImage = "url(" + playstatuslayer.dataset.bckgrndPause + ")";
        break;
      case 'stopped':
        showPlay &= true;
        showPause &= false;
        enableStop &= false;
        playstatuslayer.style.backgroundImage = "url(" + playstatuslayer.dataset.bckgrndStop + ")";
        break;
      default:
        console.log("Invalid playback status " + message.status)
    }
  }
  if (message.player != undefined) {
    showBack &= (message.player.canGoPrevious == undefined || message.player.canGoPrevious);
    showFor &= (message.player.canGoNext == undefined || message.player.canGoNext);
    showPlay &= (message.player.canPlay == undefined || message.player.canPlay);
    showPause &= (message.player.canPause == undefined || message.player.canPause);
  }
  if (message.trackMetadata != undefined) {
    update_track_metadata(message.trackMetadata);
  }
  // decide which buttons will be used
  if (showBack) {
    backwardbtn.classList.remove("hide");
  } else {
    backwardbtn.classList.add("hide")
  }
  if (showPlay) {
    playbtn.classList.remove("hide");
  } else {
    playbtn.classList.add("hide")
  }
  if (showPause) {
    pausebtn.classList.remove("hide");
  } else {
    pausebtn.classList.add("hide")
  }
  if (showFor) {
    forwardbtn.classList.remove("hide");
  } else {
    forwardbtn.classList.add("hide")
  }
  stopbtn.disabled = !enableStop;
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

// preload playstatuslayer background images:
function preloadStatusImages() {
  preloadImages([
      playstatuslayer.dataset.bckgrndPlay,
      playstatuslayer.dataset.bckgrndPause,
      playstatuslayer.dataset.bckgrndStop
  ]);
}
