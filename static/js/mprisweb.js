var ws;
var currentTitle = document.getElementById("current")
var nextTitle = document.getElementById("next")

var url = "ws://localhost:8888/websocket";

document.onload = connect(url);
window.onbeforeunload = function() {
	ws = undefined; // don't reconnect while reloading page
};


function connect(url) {
	if (ws == undefined || ws.readyState == ws.CLOSED)	 {
		ws = new WebSocket(url);
		ws.onopen = onopen;
		ws.onmessage = onmessage;
		ws.onclose = onclose;
		ws.onerror = function (error) { // TODO reconnect
			console.log('WebSocket Error ' + error);
		};
	}
}

function onopen() {
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
};

function onclose() {
	if (ws != undefined && ws.readyState == ws.CLOSED) {
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
  // DEBUG:
  // var titles = document.getElementsByClassName('titles');
  // for (var i = 0, l = titles.length; i < l; i++) {
  //   titles[i].classList.add('fadeout');
  // }
}

function play() {
  send("play");
}

function pause() {
  send("pause");
}

function forward() {
  send("forward");
  // DEBUG:
  // var titles = document.getElementsByClassName('titles');
  // for (var i = 0, l = titles.length; i < l; i++) {
  //   titles[i].classList.add('fadein');
  // }
}

function stop() {
  send("stop");
  // DEBUG:
  // var titles = document.getElementsByClassName('titles');
  // for (var i = 0, l = titles.length; i < l; i++) {
  //   titles[i].classList.remove('fadein');
  //   titles[i].classList.remove('fadeout');
  // }
}
