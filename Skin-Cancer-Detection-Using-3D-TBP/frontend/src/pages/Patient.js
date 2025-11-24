import React, {useEffect, useState} from 'react';
import { getDetections, uploadImage, getGradcam } from '../api';
import { useParams } from 'react-router-dom';

export default function Patient(){
  const { id } = useParams();
  const [dets, setDets] = useState([]);
  useEffect(()=>{ fetch(); },[]);
  const fetch = async()=>{ const res = await getDetections(id, localStorage.getItem('access_token')); setDets(res || []); };
  const onFile = async(e)=>{
    const file = e.target.files[0];
    const res = await uploadImage(id, file, localStorage.getItem('access_token'));
    alert(JSON.stringify(res));
    fetch();
  };
  const showGrad = async(did)=>{
    const res = await getGradcam(did, localStorage.getItem('access_token'));
    alert('GradCAM saved at: ' + res.gradcam_path);
    window.open(res.gradcam_path, '_blank');
  };
  return (<div>
    <h2>Patient {id}</h2>
    <input type="file" onChange={onFile}/>
    <ul className="list-group mt-3">
      {dets.map(d=> <li key={d.id} className="list-group-item">
        <div><strong>{d.prediction}</strong> ({Math.round(d.confidence*100)}%)</div>
        <div><button className="btn btn-sm btn-outline-primary mt-1" onClick={()=>showGrad(d.id)}>Show Grad-CAM</button></div>
      </li>)}
    </ul>
  </div>);
}
