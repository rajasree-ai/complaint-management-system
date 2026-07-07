import {
BrowserRouter,
Routes,
Route
}
from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import UploadMaterial from "./pages/UploadMaterial";

function App(){

return(

<BrowserRouter>

<Routes>

<Route
path="/"
element={<Login/>}
/>

<Route
path="/dashboard"
element={<Dashboard/>}
/>

<Route
path="/upload"
element={<UploadMaterial/>}
/>

</Routes>

</BrowserRouter>

);
}

export default App;