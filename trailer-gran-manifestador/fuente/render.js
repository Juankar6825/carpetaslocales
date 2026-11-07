const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
(async()=>{
 const mode=process.argv[2];const dir=process.argv[3];
 const b=await chromium.launch({args:['--allow-file-access-from-files']});
 const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('console',m=>console.log('PAGE',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('file://'+path.join(dir,'trailer.html'));await p.evaluate(()=>window.ready);
 const el=await p.$('#c');
 if(mode==='stills'){
  for(const t of process.argv.slice(4).map(Number)){await p.evaluate(t=>renderFrame(t),t);await el.screenshot({path:`${dir}/stills/s_${t}.jpg`,type:'jpeg',quality:80});}
 }else{
  const fps=30,N=37*fps;
  const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',''+fps,'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',`${dir}/video_noaudio.mp4`],{stdio:['pipe','ignore','inherit']});
  for(let i=0;i<N;i++){await p.evaluate(t=>renderFrame(t),i/fps);const buf=await el.screenshot({type:'jpeg',quality:95});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%150==0)console.log('frame',i);}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));
 }
 await b.close();
})();
