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
  preloadImages();
};
window.onbeforeunload = function() {
  ws = undefined; // don't reconnect while reloading page
};
window.onresize = onWindowResize;


Array.prototype.min = function() {
  var min = this[0];
  for (var i = 1; i < this.length; i++) if (this[i] < min) min = this[i];
  return min;
}

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

function update_track_metadata(meta) {
  text = "";
  if (meta.trackNumber != undefined && meta.trackNumber != "") {
      text += "<p><b>Track Nr.:</b> " + meta.trackNumber + "</p>";
  }
  if (meta.title != undefined && meta.title != "") {
      text += "<p><b>Title:</b> " + meta.title + "</p>";
  }
  if (meta.album != undefined && meta.album != "") {
      text += "<p><b>Album:</b> " + meta.album + "</p>";
  }
  if (meta.albumArtist != undefined && meta.albumArtist != "") {
      text += "<p><b>Album Artist:</b> " + meta.albumArtist + "</p>";
  }
  if (meta.artist != undefined && meta.artist != "") {
      text += "<p><b>Artist:</b> " + meta.artist + "</p>";
  }
  if (meta.audioBpm != undefined && meta.audioBpm != "") {
      text += "<p><b>Audio BPM:</b> " + meta.audioBpm + "</p>";
  }
  if (meta.userRating != undefined && meta.userRating != "") {
      text += "<p><b>User Rating:</b> " + meta.userRating + "</p>";
  }
  if (meta.autoRating != undefined && meta.autoRating != "") {
      text += "<p><b>Auto Rating:</b> " + meta.autoRating + "</p>";
  }
  if (meta.comment != undefined && meta.comment != "") {
      text += "<p><b>Comment:</b> " + meta.comment + "</p>";
  }
  if (meta.composer != undefined && meta.composer != "") {
      text += "<p><b>Composer:</b> " + meta.composer + "</p>";
  }
  if (meta.discNumber != undefined && meta.discNumber != "") {
      text += "<p><b>Disc Nr.:</b> " + meta.discNumber + "</p>";
  }
  if (meta.genre != undefined && meta.genre != "") {
      text += "<p><b>Genre:</b> " + meta.genre + "</p>";
  }
  if (meta.lyricist != undefined && meta.lyricist != "") {
      text += "<p><b>Lyricist:</b> " + meta.lyricist + "</p>";
  }
  if (meta.url != undefined && meta.url != "") {
      text += "<p><b>URL:</b> " + meta.url + "</p>";
  }
  trackDetails.getElementsByClassName("well")[0].innerHTML = text;

  if (meta.art == undefined) {
   meta.art = "";
  }
  if (meta.art != "") {
    artimagelayer.style.backgroundImage = "url(" + meta.art + ")";
    artimagelayer.classList.add("contains-image");
  } else {
    setTimeout(lazy_remove_artimage(), 1000);
    artimagelayer.classList.remove("contains-image");
  }
  for (var i = 0; i < artimages.length; i++) {
    artimages[i].src = meta.art;
  }
}

function lazy_remove_artimage() {
  // for nicer animations: keep image until layer above is completely faded in
  if (artimages[0].src == "") {
    // indicator, if there is an artimage
    artimagelayer.style.backgroundImage = "";
  }
}

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
  for (var i = 0; i < statusbadges.length; i++) {
    if (ws.readyState == ws.OPEN) {
      statusbadges[i].className = "statusbadge statusbadge-ok";
    } else if (ws.readyState == ws.CONNECTING || ws.readyState == ws.CLOSING) {
      statusbadges[i].className = "statusbadge statusbadge-progress";
    } else {
      statusbadges[i].className = "statusbadge statusbadge-problem";
    }
  }
}

// preload playstatuslayer background images:
function preloadImages() {
  img = new Image();
  img.src = playstatuslayer.dataset.bckgrndPlay;
  img.src = playstatuslayer.dataset.bckgrndPause;
  img.src = playstatuslayer.dataset.bckgrndStop;
}

// scroll banner animations
// TODO

function onWindowResize() {
  var arr = [artimagelayer.offsetWidth, playstatuslayer.offsetWidth, window.innerHeight];
  h = arr.min() + "px";
  artimagelayer.style.maxHeight = h;
  playstatuslayer.style.maxHeight = h;
}
