import React from "react";

function Notification({
  title,
  message
}) {

  return (

    <div
      className="notification"
    >

      <h4>{title}</h4>

      <p>{message}</p>

    </div>

  );
}

export default Notification;