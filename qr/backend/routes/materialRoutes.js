const express = require("express");

const router = express.Router();

const upload =
require("../config/multer");

const auth =
require("../middleware/authMiddleware");

const role =
require("../middleware/roleMiddleware");

const {
  getMaterials,
  uploadMaterial
}
=
require("../controllers/materialController");

router.get(
  "/",
  auth,
  getMaterials
);

router.post(
  "/upload",
  auth,
  role("teacher", "admin"),
  upload.single("file"),
  uploadMaterial
);

module.exports = router;