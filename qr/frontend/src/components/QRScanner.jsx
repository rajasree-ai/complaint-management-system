import React, { useState } from "react";
import { QrReader } from "react-qr-reader";

function QRScanner() {

  const [result, setResult] =
    useState("");

  return (
    <div>

      <h2>Scan Classroom QR</h2>

      <QrReader
        constraints={{
          facingMode: "environment"
        }}
        onResult={(scanResult) => {

          if (scanResult) {

            setResult(
              scanResult?.text
            );

            window.location.href =
              scanResult?.text;
          }

        }}
      />

      <p>{result}</p>

    </div>
  );
}

export default QRScanner;