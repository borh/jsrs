// TODO: http://mae.chab.in/archives/2307

// TODO: How long a gap between playback of sound files (if we decide to play them back-to-back)?
// TODO: Play back A/B tone before each file.

"use strict";

document.addEventListener("DOMContentLoaded", function(event) {
  var controls = function(audio_id, play_id, pause_id) {
    document.getElementById(play_id).onclick = function() {
      console.log('played');
      document.getElementById(audio_id).play();
      document.getElementById(play_id).classList.toggle('hide');
      document.getElementById(pause_id).classList.toggle('hide');
    };

    document.getElementById(pause_id).onclick = function() {
      console.log('paused');
      document.getElementById(audio_id).pause();
      document.getElementById(pause_id).classList.toggle('hide');
      document.getElementById(play_id).classList.toggle('hide');
    };

    // FIXME
    document.getElementById(audio_id).on = function(e) {
      console.log(e);
      if (e === 'ended') {
        document.getElementById(pause_id).classList.toggle('hide');
        document.getElementById(play_id).classList.toggle('hide');
        document.getElementById(audio_id).load();
      }
    };
  };

  controls('a', 'a-play-button', 'a-pause-button');
  controls('b', 'b-play-button', 'b-pause-button');
});
