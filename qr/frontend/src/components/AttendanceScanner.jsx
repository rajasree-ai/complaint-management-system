import React from "react";
import { QrReader } from "react-qr-reader";
import axios from "axios";

function AttendanceScanner() {

  const markAttendance =
    async (classroom) => {

      const token =
        localStorage.getItem("token");

      await axios.post(
        "http://localhost:5000/api/attendance/mark",
        {
          classroom
        },
        {
          headers: {
            Authorization: token
          }
        }
      );

      alert(
        "Attendance Marked"
      );
    };

  return (

    <div>

      <h2>
        Attendance Scanner
      </h2>

      <QrReader
        onResult={(result) => {

          if (result) {

            markAttendance(
              result.text
            );
          }

        }}
      />

    </div>
  );
}

export default AttendanceScanner;