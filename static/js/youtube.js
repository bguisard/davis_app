// ###########################################################################
// # YOUTUBE API                                                             #
// ###########################################################################

// Loads the IFrame Player API code asynchronously.
var canvas, ctx;

function init_youtube() {
    var tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";

    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    // We will use this to replicate the video
    canvas = document.getElementById("myCanvas");
    ctx = canvas.getContext('2d');
}

// 3. Creates an <iframe> (and YouTube player)
//    after the API code downloads.
var player;

function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '390',
        width: '640',
        playerVars: {
            listType: 'playlist',
            list: 'PLxvdl9FFFL8ggc7ZCJhZrKMNhQxCGnZqK',
            autoplay: 1,
            controls: 1,
            showinfo: 0,
            modestbranding: 1,
            loop: 1,
            fs: 0,
            cc_load_policy: 0,
            iv_load_policy: 3,
            autohide: 1
        },
        events: {
            'onReady': onPlayerReady
            // 'onStateChange': onPlayerStateChange
        }
    });
}

// 4. The API will call this function when the video player is ready.
function onPlayerReady(event) {
    event.target.playVideo();
    event.target.mute();
}

// 5. The API calls this function when the player's state changes.
//    The function indicates that when playing a video (state=1),
//    the player should play for six seconds and then stop.
var done = false;
function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.PLAYING && !done) {
        setTimeout(stopVideo, 6000);
        done = true;
    }
}
function stopVideo() {
    player.stopVideo();
}

// ###########################################################################
// # REPLICATING TO CANVAS                                                   #
// ###########################################################################

namespace = '/';

// Connect to the Socket.IO server.
// The connection URL has the following format:
//     http[s]://<domain>:<port>[/<namespace>]
// var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

function snapshot() {
    if(!done) {
        var resizedWidth = 480;
        var resizedHeight = 360;
        canvas.width = resizedWidth;
        canvas.height = resizedHeight;

        // Draws current image from the video element into the canvas
        ctx.drawImage(player, 0, 0, 480, 360);
        var currentFrame = canvas.toDataURL("image/jpeg");
        $.post("/youtube_admin", { frame_data: currentFrame, is_stream: is_stream });
    }
}

// snapshotTimer = setInterval(snapshot, 5000);

// Event handler for new connections.
// The callback function is invoked when a connection with the
// server is established.
socket.on('frame', function(data) {
    socket.emit('frame', frame);
});