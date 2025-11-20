// server.js
const express = require("express");
const cors = require("cors");
const multer = require("multer");
const axios = require("axios");
const path = require("path");
const fs = require("fs");
const FormData = require("form-data");

const app = express();
app.use(cors());
app.use(express.json());

// uploads folder
const uploadsDir = path.join(__dirname, "uploads");
if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir, { recursive: true });

// Multer
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadsDir),
  filename: (req, file, cb) =>
    cb(null, `${Date.now()}-${Math.random()}${path.extname(file.originalname)}`)
});
const upload = multer({ storage });

// Health check
app.get("/", (req, res) => res.json({ status: "Node OK" }));

// Analyze API
app.post("/analyze", upload.single("resume"), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: "No resume uploaded" });

  const form = new FormData();
  form.append("resume", fs.createReadStream(req.file.path)); // FIXED
  form.append("target_role", req.body.target_role || "");
  form.append("resume_text", req.body.resume_text || "");

  try {
    const response = await axios.post("http://127.0.0.1:8000/analyze", form, {
      headers: form.getHeaders()
    });

    fs.unlinkSync(req.file.path);

    res.json(response.data);

  } catch (err) {
    console.error("Python Error:", err.response?.data || err.message);
    res.status(500).json({ error: "Python backend error" });
  }
});

// Start server
app.listen(5000, () => console.log("Node running on port 5000"));
