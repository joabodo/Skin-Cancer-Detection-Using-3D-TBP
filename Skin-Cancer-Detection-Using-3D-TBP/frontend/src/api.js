import axios from 'axios';
const API_BASE = process.env.REACT_APP_API || '';

export async function register(email,password){
  return axios.post(`${API_BASE}/auth/register`, {email,password}).then(r=>r.data);
}
export async function login(email,password){
  return axios.post(`${API_BASE}/auth/login`, {email,password}).then(r=>r.data);
}
export async function verify2fa(token, code){
  return axios.post(`${API_BASE}/auth/verify-2fa`, {token, totp_code: code}).then(r=>r.data);
}
export async function getPatients(){
  return axios.get(`${API_BASE}/patients`).then(r=>r.data);
}
export async function createPatient(name,dob,token){
  return axios.post(`${API_BASE}/patients`, {name,dob}, {headers: {Authorization: `Bearer ${token}`}}).then(r=>r.data);
}
export async function uploadImage(patientId, file, token){
  const fd = new FormData(); fd.append('file', file);
  return axios.post(`${API_BASE}/predict/upload/${patientId}`, fd, {headers: {Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data'}}).then(r=>r.data);
}
export async function getDetections(patientId, token){
  return axios.get(`${API_BASE}/patients/${patientId}/detections`, {headers: {Authorization: `Bearer ${token}`}}).then(r=>r.data);
}
export async function getGradcam(detectionId, token){
  return axios.post(`${API_BASE}/predict/gradcam/${detectionId}`, {}, {headers: {Authorization: `Bearer ${token}`}}).then(r=>r.data);
}
export async function uploadModel(file, token){
  const fd = new FormData(); fd.append('file', file);
  return axios.post(`${API_BASE}/admin/upload-model`, fd, {headers: {Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data'}}).then(r=>r.data);
}
