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
    // Include the message so the client can show it
    serverMessage: `Server received your message:`,
  });
});

// 5) Catch-all route for your React SPA
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "build", "index.html"));
});

const PORT = process.env.PORT || 5002;
app.listen(PORT, () => {
  console.log("Server running at http://localhost:5002");
});
