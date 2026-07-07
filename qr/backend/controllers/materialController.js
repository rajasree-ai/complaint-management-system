const Material = require("../models/Material");

exports.getMaterials = async (req, res) => {

  try {

    const materials =
      await Material.find()
        .populate("uploadedBy");

    res.json(materials);

  } catch (error) {
    res.status(500).json(error);
  }
};

exports.uploadMaterial = async (req, res) => {

  try {

    const material = new Material({
      title: req.body.title,
      subject: req.body.subject,
      fileUrl: req.file.path,
      uploadedBy: req.user.id
    });

    await material.save();

    res.status(201).json(material);

  } catch (error) {
    res.status(500).json(error);
  }
};