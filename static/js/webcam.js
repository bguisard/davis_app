//--------------------
// GET USER MEDIA CODE
//--------------------
navigator.getUserMedia = (navigator.getUserMedia || navigator.webkitGetUserMedia ||
                            navigator.mozGetUserMedia || navigator.msGetUserMedia);
var video;
var webcamStream;
var is_stream = 0;

var constraints = {
  audio: false,
  video: true
};

function startWebcam() {
    if (navigator.getUserMedia) {
        navigator.getUserMedia (
            // constraints
            {
            video: true,
            audio: false
            },
            // successCallback
            function(localMediaStream) {
                video = document.querySelector('video');
                video.src = window.URL.createObjectURL(localMediaStream);
                webcamStream = localMediaStream;
            },
            // errorCallback
            function(err) {
                console.log("The following error occured: " + err);
            }
        );
        is_stream = 1;
    } else {
        console.log("getUserMedia not supported");
    }
}

function stopWebcam() {
    webcamStream.getVideoTracks()[0].stop();
    is_stream = 0;
}

//---------------------
// TAKE A SNAPSHOT CODE
//---------------------
var canvas, ctx;
function init() {
    // Get the canvas and obtain a context for
    // drawing in it
    canvas = document.getElementById("myCanvas");
    ctx = canvas.getContext('2d');
}

namespace = '/';

// Connect to the Socket.IO server.
// The connection URL has the following format:
//     http[s]://<domain>:<port>[/<namespace>]
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

function snapshot() {
    if(webcamStream) {
        var resizedWidth = 480;
        var resizedHeight = 360;
        canvas.width = resizedWidth;
        canvas.height = resizedHeight;

        // Draws current image from the video element into the canvas
        ctx.drawImage(video, 0, 0, 480, 360);
        var currentFrame = canvas.toDataURL("image/jpeg");
        $.post("/webcam_admin", { frame_data: currentFrame, is_stream: is_stream });
    }
}

snapshotTimer = setInterval(snapshot, 100);

// Event handler for new connections.
// The callback function is invoked when a connection with the
// server is established.
socket.on('frame', function(data) {
    socket.emit('frame', frame);
});