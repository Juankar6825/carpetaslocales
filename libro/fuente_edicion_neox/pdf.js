const {chromium}=require('playwright');const path=require('path');
(async()=>{const [inp,out]=process.argv.slice(2);const b=await chromium.launch();const p=await b.newPage();
p.on('pageerror',e=>console.log('ERR',e.message));p.on('requestfailed',r=>console.log('FAIL',r.url()));
await p.goto('file://'+path.resolve(inp),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
await p.pdf({path:out,preferCSSPageSize:true,printBackground:true,tagged:true,outline:true});await b.close()})();
