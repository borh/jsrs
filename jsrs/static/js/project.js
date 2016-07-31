'use strict';

document.addEventListener('DOMContentLoaded', function(event) {
  init();
  var ua = browserDetect();
  if (document.querySelector('.autoplay') && !/mobile/i.test(ua)) {
    console.log('Autoplaying audio...');
    document.getElementById('play-button').click();
  }
});

function browserDetect() {
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

var display;

function init() {
  display = document.getElementById('play-button');
  if (display)
    display.addEventListener('click', handleClick, false);
}

function handleClick(event) {
  display.removeEventListener('click', handleClick, false);
  var myApp = new myNameSpace.MyApp();
}

this.myNameSpace = this.myNameSpace || {};
(function() {
  function MyApp() {
    this.init();
  }

  MyApp.prototype = {
    inited: false,
    loadProxy: null,
    aSound: null,
    bSound: null,

    init: function() {
      console.log('init called');

      if (!createjs.Sound.initializeDefaultPlugins()) { console.log('initializeDefaultPlugins'); return; }

      var sounds = [
        {id: 'a', src: document.getElementById('a').getAttribute('src')},
        {id: 'b', src: document.getElementById('b').getAttribute('src')}
      ];

      document.getElementById('play-button').innerHTML = 'ロード中';
      this.loadProxy = createjs.proxy(this.handleLoad, this);
      createjs.Sound.addEventListener('fileload', this.loadProxy);
      createjs.Sound.registerSounds(sounds);
    },

    // handleLoad is called for each sound that is registered.
    handleLoad: function(event) {
      if (this.inited) { return; }

      console.log('handleLoad called');

      this.aSound = createjs.Sound.play('a');

      var p = document.getElementById('play-button');
      p.classList.toggle('active');
      p.classList.toggle('disabled');
      p.disabled = true;
      p.innerHTML = 'Ａを再生中';

      if (this.aSound.playState !== 'playSucceeded') {
        console.log('Audio playback failed for ' + this.aSound);
        console.log(this.aSound);
        this.playFallback('a', this.playB);
      } else {
        this.aSound.on('complete', this.playB, this);
      }

      this.inited = true;
    },

    playB: function(event) {
      console.log('aSound.on complete called');
      this.bSound = createjs.Sound.play('b');
      document.getElementById('play-button').innerHTML = 'Ｂを再生中';

      if (this.bSound.playState !== 'playSucceeded') {
        console.log('Audio playback failed for ' + this.bSound);
        console.log(this.bSound);
        this.playFallback('b', window.myNameSpace.MyApp.prototype.enableRatings);
      } else {
        this.bSound.on('complete', window.myNameSpace.MyApp.prototype.enableRatings, this);
      }
    },

    enableRatings: function(event) {
      console.log('bSound.on complete called');
      document.getElementById('play-button').classList.toggle('hide');
      document.getElementById('rating').classList.toggle('hide');
      window.addEventListener('keydown', function(e) {
        var code = e.keyCode;
        if      (code == 65) // a
          document.getElementById('id_a_gt_b_1').click();
        else if (code == 66) // b
          document.getElementById('id_a_gt_b_2').click();
        else if (code == 32) // <space>
          document.getElementById('play-button').click();
      }, false);
      createjs.Sound.removeEventListener('fileload', this.loadProxy);
      createjs.Sound.removeEventListener('complete', this.playa);
      createjs.Sound.removeEventListener('complete', this.playb);
      this.aSound.destroy();
      this.bSound.destroy();
    },

    playFallback: function(audio_id, callback) {
      console.log('Falling back to plain js audio playback');
      var audio_src = document.getElementById(audio_id).getAttribute('src');
      var e = new Audio(audio_src);
      if (callback)
        e.addEventListener('ended', callback, this);
      e.play();
    }
  }

  myNameSpace.MyApp = MyApp;
}());
