/**
 * Original Created by Andrew D.Laptev<a.d.laptev@gmail.com> on 30.03.15.
 */

const app = require("express")(),
  server = require("http").Server(app),
  io = require("socket.io")(server),
  rtsp = require("../lib/rtsp-ffmpeg");
// use rtsp = require('rtsp-ffmpeg') instead if you have install the package
server.listen(6147, function () {
  console.log("Listening on localhost:6147");
});

//NUMCAMERAS TO BE UPDATED BY NUMBER OF MODULES IN SWARM
var numCameras = 36;
var camsList = [];
for (let step = 0; step < numCameras; step++) {
  var host = 200 + step;
  var port = 8080 + step;
  camsList.push("http://192.168.0." + host + ":" + port);
}

console.log(camsList);

var cams = camsList.map(function (uri, i) {
  var stream = new rtsp.FFMpeg({
    input: uri,
    resolution: "200x200",
    quality: 3,
    rate: 30,
  });
  stream.on("start", function () {
    console.log("stream " + i + " started");
  });
  stream.on("stop", function () {
    console.log("stream " + i + " stopped");
  });

  return stream;
});

cams.forEach(function (camStream, i) {
  var ns = io.of("/cam" + i);
  ns.on("connection", function (wsocket) {
    console.log("connected to /cam" + i);
    var pipeStream = function (data) {
      wsocket.emit("data", data);
    };
    camStream.on("data", pipeStream);

    wsocket.on("disconnect", function () {
      console.log("disconnected from /cam" + i);
      camStream.removeListener("data", pipeStream);
    });
  });
});

io.on("connection", function (socket) {
  socket.emit("start", cams.length);
  socket.on("command", (msg) => {
    io.emit("message", msg);
  });
});

app.get("/", function (req, res) {
  res.sendFile(__dirname + "/indexmpeg.html");
});
