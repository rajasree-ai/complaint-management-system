require("dotenv").config();

const express = require("express");
const path = require("path");
const cors = require("cors");
const connectDB = require("./config/db");
const authRoutes = require("./routes/authRoutes");
const materialRoutes = require("./routes/materialRoutes");

const app = express();

app.use(cors());
app.use(express.json());
// Serve uploaded files statically at /uploads
app.use(
  "/uploads",
  express.static(path.join(__dirname, "uploads"))
);
app.use("/api/auth", authRoutes);
app.use("/api/materials", materialRoutes);

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

connectDB().catch(() => process.exit(1));

app.listen(5000, () => {
  console.log("Server running on port 5000");
});
