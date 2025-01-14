const path = require("path");
const express = require("express");
const app = express();

// 1) Parse JSON from incoming requests
app.use(express.json());

// 2) Serve the built React app
app.use(express.static(path.join(__dirname, "build")));

// 3) Example GET route
app.get("/api/data", (req, res) => {
  res.json({ message: "This is data from the Node.js server!" });
});

// 4) POST route to receive data from React
app.post("/api/data", (req, res) => {
  const { message } = req.body;
  console.log("Received from client:", message);

  // Send back a JSON response
  res.json({
    success: true,
    received: message,
    serverMessage: `${message}`,
  });
});

// 5) Catch-all route for your React SPA
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "build", "index.html"));
});

// Start the server
const PORT = process.env.PORT || 5001;
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
