const multer = require("multer");

const storage = multer.diskStorage({

  destination: function (req, file, cb) {
    cb(null, "uploads/");
  },

  filename: function (req, file, cb) {

    cb(
      null,
      Date.now() +
      "-" +
      file.originalname
    );
  }
});

const fileFilter = (req, file, cb) => {

  const allowedTypes = [

    "application/pdf",

    "application/vnd.openxmlformats-officedocument.presentationml.presentation",

    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ];

  if (allowedTypes.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(new Error("Invalid File Type"));
  }
};

module.exports =
multer({
  storage,
  fileFilter
});