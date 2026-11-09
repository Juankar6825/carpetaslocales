const {chromium}=require('playwright');const path=require('path');
(async()=>{const dir=process.argv[2];const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage({viewport:{width:1920,height:1920}});
p.on('pageerror',e=>console.log('ERR',e.message));await p.goto('file://'+path.join(dir,'covers.html'));await p.evaluate(()=>window.ready);
for(let i=0;i<3;i++)for(const v of [false,true]){await p.evaluate(([i,v])=>draw(i,v),[i,v]);const el=await p.$('#c');await el.screenshot({path:`${dir}/raw_${i+1}_${v?'v':'h'}.png`})}
await b.close()})();
