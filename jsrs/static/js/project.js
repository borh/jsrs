// TODO: http://mae.chab.in/archives/2307

// TODO: How long a gap between playback of sound files (if we decide to play them back-to-back)?
// TODO: Play back A/B tone before each file.

"use strict";

var switcharoo = function(e, dummyUrl) {
  var originalSrc = e.src;
  e.src = dummyUrl;
  e.play();
  e.src = originalSrc;
}

document.addEventListener("DOMContentLoaded", function(event) {

  // Workaround for broken audio in mobile Chrome (https://bugs.chromium.org/p/chromium/issues/detail?id=178297)
  if (document.getElementById('dummy')) {
    var dummy_url = document.getElementById('dummy').src;
    switcharoo(document.getElementById('a'), dummy_url);
  }
  // End of workaround

  if (document.getElementById('play-button')) {
    document.getElementById('play-button').onclick = function() {
      if (document.getElementById('play-button').classList.contains('active')) {
        return;
      }
      document.getElementById('a').play();
      switcharoo(document.getElementById('b'), dummy_url);
      // console.log(document.getElementById('a').currentTime);
      // document.getElementById('a').addEventlistener('loadedmetadata', function() {
      //   console.log(document.getElementById('a').duration);
      // });

      document.getElementById('play-button').classList.toggle('active');
      document.getElementById('play-button').classList.toggle('disabled');
      document.getElementById('play-button').innerHTML = 'Ａを再生中';
    };

    document.getElementById('a').onended = function(e) {
      document.getElementById('b').play();
      document.getElementById('play-button').innerHTML = 'Ｂを再生中';
    };

    document.getElementById('b').onended = function(e) {
      document.getElementById('play-button').classList.toggle('hide');
      document.getElementById('rating').classList.toggle('hide');
    };
  }
});
