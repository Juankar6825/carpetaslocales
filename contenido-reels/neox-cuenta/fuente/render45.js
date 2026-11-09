const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
(async()=>{const [dir,mode,...ts]=process.argv.slice(2);const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage({viewport:{width:1080,height:1920}});p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+path.join(dir,'neox45.html'));await p.evaluate(()=>window.ready);const el=await p.$('#c');
if(mode==='stills'){for(const t of ts){await p.evaluate(t=>renderFrame(t),+t);await el.screenshot({path:`${dir}/st_${t}.jpg`,type:'jpeg',quality:80})}}
else{const tot=await p.evaluate(()=>D.tot);const fps=30,N=Math.round(tot*fps);const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',''+fps,'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p',`${dir}/noaudio45.mp4`],{stdio:['pipe','ignore','inherit']});
 for(let i=0;i<N;i++){await p.evaluate(t=>renderFrame(t),i/fps);const buf=await el.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r))}ff.stdin.end();await new Promise(r=>ff.on('close',r))}
await b.close()})();
