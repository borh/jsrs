// TODO: http://mae.chab.in/archives/2307

// TODO: How long a gap between playback of sound files (if we decide to play them back-to-back)?
// TODO: Play back A/B tone before each file.

"use strict";

// TODO detect browsers

var browserDetect = function() {
  var ua = navigator.userAgent;
  var detected;
  if (/Mobile|mobile/i.test(ua) && /Chrome|iPad|iPod|iPhone/i.test(ua) && !/Safari/i.test(ua))
    detected = 'mobile chrome';
  else if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile|mobile|CriOS/i.test(ua))
    detected = 'mobile';
  else if (/Chrome/i.test(ua))
    detected = 'chrome';
  else
    detected = 'other';
  console.log('Detected browser ' + detected + ' based on UA: ' + ua);
  return detected;
}

var switcharoo = function(e, dummyUrl) {
  var originalSrc = e.src;
  e.src = dummyUrl;
  try {
    e.play();
    e.src = originalSrc;
  }
  catch (err) {
    console.log('Ignoring playback error: ' + err.message);
  }
}

var play_audio = function(ua, dummy_url, switched) {
  if (!switched && /mobile/i.test(ua)) {
    // Workaround for broken audio in mobile Chrome (https://bugs.chromium.org/p/chromium/issues/detail?id=178297)
    if (document.getElementById('dummy')) {
      switcharoo(document.getElementById('a'), dummy_url);
      //switcharoo(document.getElementById('b'), dummy_url);
    }
  }

  document.getElementById('play-button').onclick = function() {
    if (document.getElementById('play-button').classList.contains('active')) {
      return;
    }
    document.getElementById('a').play();
    // console.log(document.getElementById('a').currentTime);
    // document.getElementById('a').addEventlistener('loadedmetadata', function() {
    //   console.log(document.getElementById('a').duration);
    // });

    document.getElementById('play-button').classList.toggle('active');
    document.getElementById('play-button').classList.toggle('disabled');
    document.getElementById('play-button').disabled = true;
    document.getElementById('play-button').innerHTML = 'Ａを再生中';
  };

  document.getElementById('a').onended = function(e) {
    if (!switched && /mobile/i.test(ua))
      switcharoo(document.getElementById('b'), dummy_url);

    document.getElementById('b').play();
    document.getElementById('play-button').innerHTML = 'Ｂを再生中';
  };

  document.getElementById('b').onended = function(e) {
    document.getElementById('play-button').classList.toggle('hide');
    document.getElementById('rating').classList.toggle('hide');
  };
}

document.addEventListener("DOMContentLoaded", function(event) {

  var ua = browserDetect();
  var dummy_url = document.getElementById('dummy').src;
  var switched = false;

  if (document.getElementById('play-button')) {
    play_audio(ua, dummy_url, switched);

  //window.setTimeout(function() {
  // NOTE: Cannot autoplay on mobile.
  if (document.querySelector('.autoplay') && !/mobile/i.test(ua)) {
    console.log('Autoplaying audio...');
    document.getElementById('play-button').click();
  } else if (document.querySelector('.autoplay') && /mobile/i.test(ua)) {
    console.log('Autoplaying audio on mobile using touchend...');
    addEventListener('touchend', function (e) {
      console.log('.');
      play_audio(ua, dummy_url, switched);
      //soundHandle.src = 'audio.mp3';
      //soundHandle.loop = true;
      //soundHandle.play();
      //soundHandle.pause();
    });
  }

  //}, 200);
  }
});
