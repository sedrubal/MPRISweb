/* UI related functions */

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

// scroll banner animations
// TODO

function onWindowResize() {
  var arr = [artimagelayer.offsetWidth, playstatuslayer.offsetWidth, window.innerHeight];
  h = arr.min() + "px";
  artimagelayer.style.maxHeight = h;
  playstatuslayer.style.maxHeight = h;
}
