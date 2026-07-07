const mongoose =
require("mongoose");

const SubjectSchema =
new mongoose.Schema({

  subjectCode: {
    type: String,
    required: true
  },

  subjectName: {
    type: String,
    required: true
  },

  semester: Number,

  department: String
});

module.exports =
mongoose.model(
  "Subject",
  SubjectSchema
);