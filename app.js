const DATA_URL = "data/prices.json";
const ITEMS = [["apple","Apple","🍎","Apple"],["pear","Pear","🍐","Pear"],["plum","Plum","🟣","Plum"],["peach","Peach","🍑","Peach"],["tomato","Tomato","🍅","Tomato"],["cabbage","Cabbage","🥬","Cabbage"],["cauliflower","Cauliflower","🥦","Cauliflo."],["potato","Potato","🥔","Potato"],["onion","Onion","🧅","Onion"],["carrot","Carrot","🥕","Carrot"]];
let data=null, report=""; const $=id=>document.getElementById(id);
const MARKET_LABELS={"SMY Bhuntar":"Bhuntar","PMY Kullu":"Kullu","SMY Khegsu":"Khegsu","Kullu":"Kullu Mandi","Takoli":"Takoli"};
const today=()=>new Intl.DateTimeFormat("en-CA",{timeZone:"Asia/Kolkata",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
const fmt=n=>Number.isFinite(n)?n.toFixed(1):"-";
const priceSummary=r=>{if(!r)return null;const min=Number(r.min_price_kg),modal=Number(r.modal_price_kg),max=Number(r.max_price_kg);if(![min,modal,max].some(Number.isFinite))return null;return `Min ${fmt(min)} | Modal ${fmt(modal)} | Max ${fmt(max)}`};
function buildReport(){const mains=data.main_markets||[], comps=data.comparison_markets||[];const available=ITEMS.filter(([key])=>Object.values(data.prices[key]||{}).some(Boolean));const marketSummary=(key,market)=>priceSummary(data.prices[key]?.[market]);const label=market=>MARKET_LABELS[market]||market;let t=`📊 *Mandi Prices (₹/kg) — Kullu district*\n${data.display_date}\nMin | Modal | Max\n\n`;const priority=[];for(const [key,name,emoji] of available){for(const market of ["SMY Bhuntar","Bandrol","Takoli","Banjar","Sundernagar","Ner Chowk","Delhi","Nashik","Jammu","Jaipur"]){const summary=marketSummary(key,market);if(summary)priority.push([name,emoji,label(market),summary])}}if(priority.length){t+="⭐ *Priority: Top Ten Markets*\n";for(const [name,emoji,market,summary] of priority)t+=`${emoji} ${name} — ${market}: ${summary}\n`;t+="\n"}for(const [key,name,emoji] of available){const rows=mains.map(m=>[label(m.display),marketSummary(key,m.display)]).filter(([,summary])=>summary);if(!rows.length)continue;t+=`${emoji} *${name}*\n`;for(const [market,summary] of rows)t+=`   ${market}: ${summary}\n`;t+="\n"}let comparisonText="",comparisonCount=0;for(const [key,name,emoji] of available){const rows=comps.map(m=>[label(m.display),marketSummary(key,m.display)]).filter(([,summary])=>summary);if(!rows.length)continue;comparisonCount++;comparisonText+=`${emoji} *${name}*\n`;for(const [market,summary] of rows)comparisonText+=`   ${market}: ${summary}\n`;comparisonText+="\n"}if(comparisonCount)t+="🌍 *Other Market Comparison*\n\n"+comparisonText;return t+"💰 Prices are per kg (converted from ₹/quintal)\n📌 Source: AGMARKNET, Govt of India"}
function render(){if(!data)return;report=buildReport();$("output").value=report;$("copyBtn").disabled=false;const current=data.date===today();$("status").textContent=data.status==="error"?"🔴 Data update failed":current?"🟢 Updated today":"🟡 Data not updated yet";$("lastUpdated").textContent=`${current?"":"⚠️ Showing last successfully updated data: "}${data.display_date} ${new Date(data.updated_at).toLocaleTimeString("en-IN",{timeZone:"Asia/Kolkata",hour:"2-digit",minute:"2-digit"})} IST`;$("debug").textContent=JSON.stringify({records:data.verification,unmatched_api_markets:data.unmatched_api_markets,unmatched_api_commodities:data.unmatched_api_commodities},null,2)}
async function load(){$("updateBtn").disabled=true;$("status").textContent="⏳ Updating…";try{const r=await fetch(`${DATA_URL}?t=${Date.now()}`);if(!r.ok)throw Error();data=await r.json();render()}catch{$("status").textContent="🔴 No price data published yet";$("lastUpdated").textContent="⚠️ Government data update failed. Run the update workflow and try again."}finally{$("updateBtn").disabled=false}}
async function copy(){try{if(navigator.clipboard)await navigator.clipboard.writeText(report);else{$("output").select();document.execCommand("copy")}$("copyBtn").textContent="✅ Copied!";setTimeout(()=>$("copyBtn").textContent="📋 Copy WhatsApp Report",2000)}catch{$("status").textContent="⚠️ Copy failed — select the report and copy it manually."}}
$("updateBtn").addEventListener("click",load);$("copyBtn").addEventListener("click",copy);load();


  // ----- Buttons -----
  const pdfBtn = document.createElement('button');
  pdfBtn.id = 'pdfBtn';
  pdfBtn.className = 'primary';
  pdfBtn.style.marginTop = '10px';
  pdfBtn.textContent = '📄 Download PDF Report';
  document.body.appendChild(pdfBtn);

  const imgBtn = document.createElement('button');
  imgBtn.id = 'imgBtn';
  imgBtn.className = 'copy';
  imgBtn.style.marginTop = '5px';
  imgBtn.textContent = '📸 Screenshot';
  document.body.appendChild(imgBtn);

  // PDF handler
  pdfBtn.addEventListener('click', () => {
    const win = window.open('', '_blank');
    win.document.write('<html><head><style>body{font-family:system-ui,sans-serif;margin:20px;}h1{color:#176b3a;}</style></head><body><h1>Kullu Mandi Prices – Top Ten Markets</h1>'+$('output').value+'<div class="note">Generated '+new Date().toLocaleString()+' IST</div></body></html>');
    win.document.close();
    win.print();
  });

  // Screenshot handler
  imgBtn.addEventListener('click', () => {
    const canvas = document.createElement('canvas');
    canvas.width = $('output').scrollWidth;
    canvas.height = $('output').scrollHeight;
    const ctx = canvas.getContext('2d');
    ctx.font = '13px ui-monospace,SFMono-Regular,Menlo,monospace';
    ctx.fillStyle = '#17251c';
    ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle = '#c6c8c8';
    ctx.fillText($('output').value, 0, 20);
    const link = document.createElement('a');
    link.download = 'kullu-mandi-'+new Date().toISOString().slice(0,10)+'.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  });
