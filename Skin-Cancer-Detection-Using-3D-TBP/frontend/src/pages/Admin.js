import React, {useState} from 'react';
import { uploadModel } from '../api';

export default function Admin(){
  const [file,setFile]=useState(null);
  const onUpload=async()=>{
    if(!file) return alert('Choose file');
    const res = await uploadModel(file, localStorage.getItem('access_token'));
    alert('Uploaded: ' + JSON.stringify(res));
  };
  return (<div>
    <h2>Admin</h2>
    <input type="file" onChange={e=>setFile(e.target.files[0])}/>
    <button className="btn btn-primary ms-2" onClick={onUpload}>Upload Model</button>
    <p>Use this to upload new model (.pth) and hot-reload backend.</p>
  </div>);
}
