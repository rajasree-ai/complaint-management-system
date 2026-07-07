import React,
{
useEffect,
useState
}
from "react";

import axios from "axios";

import Notification
from "./Notification";

function NotificationList(){

const [
notifications,
setNotifications
]
=
useState([]);

useEffect(()=>{

fetchNotifications();

},[]);

const fetchNotifications=
async()=>{

const res=
await axios.get(
"http://localhost:5000/api/notifications"
);

setNotifications(
res.data
);

};

return(

<div>

<h2>
Notifications
</h2>

{
notifications.map(
(item)=>(
<Notification
key={item._id}
title={item.title}
message={item.message}
/>
))
}

</div>

);
}

export default NotificationList;