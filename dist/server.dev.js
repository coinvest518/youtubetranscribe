"use strict";

var express = require('express'); // Correctly require express


var path = require('path');

var app = express();
var port = process.env.PORT || 5000; // Heroku assigns a dynamic port
// Serve static files from the React app's build folder

app.use(express["static"](path.join(__dirname, 'frontend/build'))); // For any other request, serve the React app

app.get('*', function (req, res) {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
}); // Start the server

app.listen(port, function () {
  console.log("Server is listening on port ".concat(port));
});