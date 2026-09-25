const API_BASE="http://127.0.0.1:8000";

async function api(path, options={}){
  const headers=options.headers||{};
  const token=localStorage.getItem("token");
  if(token) headers["Authorization"]=`Bearer ${token}`;
  options.headers=headers;
  return fetch(API_BASE+path,options);
}
function logout(){localStorage.removeItem("token");localStorage.removeItem("role");location.href="login.html";}
function requireLogin(){if(!localStorage.getItem("token"))location.href="login.html";}
function decodeToken(token){
  try{if(!token)return null;const part=token.split(".")[1];const b64=part.replace(/-/g,"+").replace(/_/g,"/");return JSON.parse(decodeURIComponent(atob(b64).split("").map(c=>"%"+("00"+c.charCodeAt(0).toString(16)).slice(-2)).join("")));}catch(e){return null;}
}
function formatApiError(data){
  if(!data)return"Request failed.";
  if(typeof data.detail==="string")return data.detail;
  if(Array.isArray(data.detail))return data.detail.map(x=>`${x.loc?x.loc.join(" → "):"Field"}: ${x.msg}`).join("<br>");
  return JSON.stringify(data);
}
function togglePassword(id,btn){
 const el=document.getElementById(id);el.type=el.type==="password"?"text":"password";
 btn.innerHTML=el.type==="password"?'<i class="bi bi-eye"></i>':'<i class="bi bi-eye-slash"></i>';
}
