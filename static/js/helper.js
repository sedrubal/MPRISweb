/* helper functions */

Array.prototype.min = function() {
  var min = this[0];
  for (var i = 1; i < this.length; i++) if (this[i] < min) min = this[i];
  return min;
}

function preloadImages(imgSrcArr) {
  for (var i = 0; i < imgSrcArr.length; i++) {
    img = new Image();
    img.src = imgSrcArr[i];
  }
}
