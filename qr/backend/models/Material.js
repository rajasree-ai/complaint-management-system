const mongoose = require("mongoose");

const MaterialSchema = new mongoose.Schema({

  title:String,

  subject:String,

  fileUrl:String,

  uploadedBy:{
    type:mongoose.Schema.Types.ObjectId,
    ref:"User"
  },

  createdAt:{
    type:Date,
    default:Date.now
  }

});

module.exports =
mongoose.model("Material",MaterialSchema);