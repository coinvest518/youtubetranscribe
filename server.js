const express = require('express'); // Correctly require express
const path = require('path');
const app = express();
const port = process.env.PORT || 5000; // Heroku assigns a dynamic port

// Serve static files from the React app's build folder
app.use(express.static(path.join(__dirname, 'frontend/build')));

// For any other request, serve the React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

// Start the server
app.listen(port, () => {
  console.log(`Server is listening on port ${port}`);
});
