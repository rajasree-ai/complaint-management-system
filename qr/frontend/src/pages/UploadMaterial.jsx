import { useState } from "react";
import axios from "axios";

function UploadMaterial() {

  const [title,
    setTitle] = useState("");

  const [subject,
    setSubject] = useState("");

  const [file,
    setFile] = useState(null);

  const handleUpload =
    async () => {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("subject", subject);
      formData.append("file", file);

      const token = localStorage.getItem("token");

      try {
        const res = await axios.post(
          "http://localhost:5000/api/materials/upload",
          formData,
          {
            headers: {
              Authorization: token
            }
          }
        );

        console.log("Upload response:", res.data);
        alert("Uploaded");
      } catch (err) {
        console.error("Upload error:", err.response || err.message || err);
        alert("Upload failed: " + (err.response?.data?.message || err.message));
      }
    };

  return (

    <div>

      <input
        placeholder="Title"
        onChange={(e) =>
          setTitle(e.target.value)}
      />

      <input
        placeholder="Subject"
        onChange={(e) =>
          setSubject(e.target.value)}
      />

      <input
        type="file"
        onChange={(e) =>
          setFile(e.target.files[0])}
      />

      <button
        onClick={handleUpload}>
        Upload
      </button>

    </div>
  );
}

export default UploadMaterial;