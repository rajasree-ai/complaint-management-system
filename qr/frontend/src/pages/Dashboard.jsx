import { useEffect, useState } from "react";
import axios from "axios";

function Dashboard() {

  const [materials,
    setMaterials] = useState([]);

  useEffect(() => {

    fetchMaterials();

  }, []);

  const fetchMaterials = async () => {

    const token =
      localStorage.getItem("token");

    const res =
      await axios.get(
        "http://localhost:5000/api/materials",
        {
          headers: {
            Authorization: token
          }
        }
      );

    setMaterials(res.data);
  };

  return (

    <div>

      <h1>Materials</h1>

      {
        materials.map((item) => (

          <div key={item._id}>

            <h3>{item.title}</h3>

            <p>{item.subject}</p>

            <a
              href={`http://localhost:5000/${item.fileUrl}`}
              target="_blank"
              rel="noreferrer"
            >
              Download
            </a>

          </div>
        ))
      }

    </div>
  );
}

export default Dashboard;