import React, {useEffect, useState} from 'react';
import { getPatients, createPatient } from '../api';
import { Link } from 'react-router-dom';

export default function Dashboard(){
  const [patients,setPatients]=useState([]);
  const [name,setName]=useState('');
  useEffect(()=>{ fetch(); },[]);
  const fetch=async()=>{ const res = await getPatients(); setPatients(res || []); };
  const add=async()=>{ await createPatient(name,null, localStorage.getItem('access_token')); setName(''); fetch(); };
  return (<div>
    <h2>Patients</h2>
    <div className="mb-2">
      <input className="form-control d-inline-block w-50" placeholder="New patient name" value={name} onChange={e=>setName(e.target.value)}/>
      <button className="btn btn-success ms-2" onClick={add}>Add</button>
    </div>
    <ul className="list-group">
      {patients.map(p=> <li key={p.id} className="list-group-item"><Link to={'/patient/'+p.id}>{p.name}</Link></li>)}
    </ul>
  </div>);
}
