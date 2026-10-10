const $ = (id) => document.getElementById(id);
const role = () => $("role").value;
const headers = () => ({"Content-Type":"application/json","X-Role":role()});
let animals = [];

function toast(message, error=false){
  const el=$("toast"); el.textContent=message; el.className="toast show"+(error?" error":"");
  setTimeout(()=>el.className="toast",3200);
}
async function api(url, options={}){
  const res=await fetch(url,{...options,headers:{...headers(),...(options.headers||{})}});
  if(!res.ok){let msg=`${res.status} ${res.statusText}`; try{const d=await res.json(); msg=d.detail||msg}catch{} throw new Error(msg)}
  return res.status===204?null:res.json();
}

function setView(id){
  document.querySelectorAll(".view").forEach(v=>v.classList.toggle("active",v.id===id));
  document.querySelectorAll(".nav").forEach(b=>b.classList.toggle("active",b.dataset.view===id));
  const titles={dashboard:"Farm Health Dashboard",animals:"Animal Files",clinical:"Clinical Actions",audit:"Audit Trail"};
  $("page-title").textContent=titles[id];
  if(id==="audit") loadAudit();
}
document.querySelectorAll(".nav").forEach(b=>b.addEventListener("click",()=>setView(b.dataset.view)));

async function loadAll(){await Promise.all([loadAnimals(),loadDashboard()]);}
async function loadDashboard(){
  const d=await api("/api/dashboard");
  const items=[
    [d.total_animals,"Animals"],[d.quarantined,"Quarantine"],[d.urgent_cases,"Urgent cases"],[d.overdue_vaccinations,"Overdue vaccines"],[d.open_outbreaks,"Outbreak flags"]
  ];
  $("metrics").innerHTML=items.map(([n,l])=>`<div class="metric"><strong>${n}</strong><span>${l}</span></div>`).join("");
}
async function loadAnimals(){
  animals=await api("/api/animals");
  $("animals-table").innerHTML=animals.map(a=>`<tr><td><b>${a.tag_id}</b></td><td>${a.name||"—"}</td><td>${a.species}</td><td>${a.enclosure}</td><td><span class="status ${a.quarantine_state}">${a.quarantine_state}</span></td><td><button class="link-btn" onclick="showAnimal(${a.id})">View file</button></td></tr>`).join("");
  if(!animals.length) $("animals-table").innerHTML=`<tr><td colspan="6" class="empty">No animals yet.</td></tr>`;
  const opts=animals.map(a=>`<option value="${a.id}">${a.tag_id} • ${a.name||a.species}</option>`).join("");
  ["illness-animal","vacc-animal","q-animal"].forEach(id=>$(id).innerHTML=opts);
  $("attention-list").innerHTML=animals.filter(a=>a.quarantine_state!=="Healthy"&&a.quarantine_state!=="Cleared").slice(0,5).map(a=>`<div class="attention"><div><b>${a.tag_id} • ${a.name||a.species}</b><small>${a.enclosure}</small></div><span class="status ${a.quarantine_state}">${a.quarantine_state}</span></div>`).join("") || `<div class="empty">No animals currently flagged.</div>`;
}
window.showAnimal=async function(id){
  const h=await api(`/api/animals/${id}/history`);
  const a=h.animal; const box=$("animal-detail"); box.classList.remove("hidden");
  box.innerHTML=`<div class="card-head"><h3>${a.tag_id} • ${a.name||a.species}</h3><span class="status ${a.quarantine_state}">${a.quarantine_state}</span></div>
  <div class="detail-grid"><div><small>Species</small><b>${a.species}</b></div><div><small>Breed</small><b>${a.breed||"—"}</b></div><div><small>Enclosure</small><b>${a.enclosure}</b></div><div><small>Weight</small><b>${a.weight_kg??"—"} kg</b></div></div>
  <p><b>History:</b> ${h.illnesses.length} illness report(s), ${h.vaccinations.length} vaccination(s), ${h.quarantine_events.length} quarantine event(s).</p>`;
  box.scrollIntoView({behavior:"smooth",block:"nearest"});
}

$("open-add-animal").addEventListener("click",()=>$("animal-dialog").showModal());
$("animal-form").addEventListener("submit",async(e)=>{
  if(e.submitter?.value==="cancel") return;
  e.preventDefault();
  try{
    await api("/api/animals",{method:"POST",body:JSON.stringify({tag_id:$("a-tag").value,name:$("a-name").value||null,species:$("a-species").value,breed:$("a-breed").value||null,sex:$("a-sex").value,age_years:$("a-age").value?Number($("a-age").value):null,enclosure:$("a-enclosure").value,weight_kg:$("a-weight").value?Number($("a-weight").value):null,temperature_c:null})});
    $("animal-dialog").close(); e.target.reset(); toast("Animal profile created"); await loadAll();
  }catch(err){toast(err.message,true)}
});

$("illness-form").addEventListener("submit",async(e)=>{
  e.preventDefault();
  const symptoms=$("symptoms").value.split(",").map(s=>s.trim()).filter(Boolean);
  try{
    const r=await api(`/api/animals/${$("illness-animal").value}/illness`,{method:"POST",body:JSON.stringify({symptoms,body_system:$("body-system").value,notes:$("illness-notes").value||null,fever:$("fever").checked})});
    toast(`Illness recorded • severity: ${r.severity}`); $("symptoms").value=""; $("illness-notes").value=""; $("fever").checked=false; await loadAll();
  }catch(err){toast(err.message,true)}
});

$("vacc-date").value=new Date().toISOString().slice(0,10);
$("vaccination-form").addEventListener("submit",async(e)=>{
  e.preventDefault();
  try{
    const r=await api(`/api/animals/${$("vacc-animal").value}/vaccinations`,{method:"POST",body:JSON.stringify({vaccine_name:$("vaccine-name").value,batch_number:$("batch").value||null,dosage:"2 ml",date_administered:$("vacc-date").value,booster_interval_days:Number($("booster-days").value),veterinarian:$("vet-name").value})});
    toast(`Vaccination saved • next due ${r.next_due_date}`); await loadDashboard();
  }catch(err){toast(err.message,true)}
});

$("quarantine-form").addEventListener("submit",async(e)=>{
  e.preventDefault();
  try{
    const r=await api(`/api/animals/${$("q-animal").value}/quarantine`,{method:"POST",body:JSON.stringify({to_state:$("q-state").value,reason:$("q-reason").value})});
    toast(`Quarantine: ${r.from_state} → ${r.to_state}`); await loadAll();
  }catch(err){toast(err.message,true)}
});

async function loadAudit(){
  try{
    const rows=await api("/api/audit");
    $("audit-table").innerHTML=rows.map(x=>`<tr><td>${new Date(x.created_at).toLocaleString()}</td><td><b>${x.action}</b></td><td>${x.entity_type}${x.entity_id?` #${x.entity_id}`:""}</td><td>${x.role}</td><td>${x.details||""}</td></tr>`).join("")||`<tr><td colspan="5" class="empty">No audit entries.</td></tr>`;
  }catch(err){$("audit-table").innerHTML=`<tr><td colspan="5" class="empty">${err.message}</td></tr>`;}
}
$("refresh-audit").addEventListener("click",loadAudit);
$("role").addEventListener("change",()=>{toast(`Role changed to ${$("role").selectedOptions[0].textContent}`); if(document.querySelector("#audit.view.active")) loadAudit();});

loadAll().catch(err=>toast(err.message,true));
