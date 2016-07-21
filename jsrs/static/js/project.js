'use strict';

var display;

function init() {
  display = document.getElementById('play-button');
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
    displayMessage: null,
    inited: false,

    init: function() {
      this.displayMessage = document.getElementById('play-button');

      if (!createjs.Sound.initializeDefaultPlugins()) {return;}

      var audioPath = '';
      var sounds = [
        {id: 'a', src: document.getElementById('a').src},
        {id: 'b', src: document.getElementById('b').src}
      ];

      this.displayMessage.innerHTML = 'ロード中';
      //createjs.Sound.alternateExtensions = ['mp3'];
      var loadProxy = createjs.proxy(this.handleLoad, this);
      createjs.Sound.addEventListener('fileload', loadProxy);
      createjs.Sound.registerSounds(sounds, audioPath);
    },

    handleLoad: function(event) {
      if (this.inited) { return; }

      var aSound = createjs.Sound.play('a');
      this.displayMessage.classList.toggle('active');
      this.displayMessage.classList.toggle('disabled');
      this.displayMessage.disabled = true;
      this.displayMessage.innerHTML = 'Ａを再生中';

      aSound.on('complete', function() {
        var bSound = createjs.Sound.play('b');
        this.displayMessage.innerHTML = 'Ｂを再生中';
        bSound.on('complete', function() {
          this.displayMessage.classList.toggle('hide');
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
        }, this);
      }, this);
      this.inited = true;
    }
  }

  myNameSpace.MyApp = MyApp;
}());

document.addEventListener('DOMContentLoaded', function(event) {
  init();
  var ua = browserDetect();
  if (document.querySelector('.autoplay') && !/mobile/i.test(ua)) {
    console.log('Autoplaying audio...');
    document.getElementById('play-button').click();
  }
});

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
