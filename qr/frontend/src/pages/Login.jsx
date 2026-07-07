import {useState} from "react";
import {useNavigate} from "react-router-dom";
import axios from "axios";

function Login(){

const [email,setEmail]=useState("");
const [password,setPassword]=useState("");
const [error,setError]=useState("");
const [loading,setLoading]=useState(false);
const navigate=useNavigate();

const handleLogin=async()=>{

setError("");
setLoading(true);

try{

const res =
await axios.post(
"/api/auth/login",
{
email,
password
}
);

localStorage.setItem(
"token",
res.data.token
);

navigate("/dashboard");

}catch(err){

setError(
err.response?.data?.message || 
"Login failed"
);

}finally{

setLoading(false);

}

};

return(

<div>

<h2>Login</h2>

{error && <p style={{color:"red"}}>{error}</p>}

<input
type="email"
placeholder="Email"
value={email}
onChange={(e)=>
setEmail(e.target.value)}
/>

<input
type="password"
placeholder="Password"
value={password}
onChange={(e)=>
setPassword(e.target.value)}
/>

<button
onClick={handleLogin}
disabled={loading}>
{loading ? "Logging in..." : "Login"}
</button>

</div>

);
}

export default Login;