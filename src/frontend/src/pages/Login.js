import React, {useState} from 'react';
import axios from 'axios';
export default function Login(){
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [msg,setMsg]=useState('');
  const handleSubmit=async(e)=>{
    e.preventDefault();
    try{
      const res=await axios.post('/api/auth/login',{email,password});
      setMsg('TwoFA token received. Check QR or code flow.');
      console.log(res.data);
    }catch(err){
      setMsg('Login failed');
    }
  };
  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input placeholder='email' value={email} onChange={e=>setEmail(e.target.value)} />
        <input placeholder='password' type='password' value={password} onChange={e=>setPassword(e.target.value)} />
        <button type='submit'>Login</button>
      </form>
      <div>{msg}</div>
    </div>
  );
}
