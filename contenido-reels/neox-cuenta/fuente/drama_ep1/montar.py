import subprocess as sp,json,os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
def run(*a):sp.run(list(a),check=True)
SH=[('v1.mp4',3.0),('v2.mp4',4.0),('v3.mp4',3.0),('v4.mp4',4.0),('v5.mp4',3.0),('v6.mp4',5.0)]
for i,(f,d) in enumerate(SH):
  run('ffmpeg','-y','-loglevel','error','-i',f,'-vf','scale=720:1280,setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=2','-t',str(d),'-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p',f'p{i}.mp4')
open('l.txt','w').write(''.join(f"file 'p{i}.mp4'\n" for i in range(len(SH))))
run('ffmpeg','-y','-loglevel','error','-f','concat','-i','l.txt','-c','copy','comp.mp4')
end=sum(d for _,d in SH);tot=round(end+2.6,2)
run('ffmpeg','-y','-loglevel','error','-i','vo.mp3','-af','atrim=0:2.25,asetpts=PTS-STARTPTS','voA.wav')
run('ffmpeg','-y','-loglevel','error','-i','vo.mp3','-af','atrim=2.8,asetpts=PTS-STARTPTS','voB.wav')
EV=[('buzz.wav',0.35,0.7),('voA.wav',3.3,1.0),('mujer.mp3',10.85,1.0),('portazo.mp3',14.0,0.9),('voB.wav',17.4,1.0)]
ins=['-stream_loop','-1','-i','../story/musV2.wav','-i','boom.wav','-i','boom.wav']
for f,_,_ in EV: ins+=['-i',f]
fc=f"[0]atrim=0:{tot},volume=0.16,afade=t=out:st={tot-1.2}:d=1.2,aformat=sample_rates=44100:channel_layouts=stereo[mu];[1]volume=0.5,aformat=sample_rates=44100:channel_layouts=stereo[b0];[2]adelay={int(end*1000)}|{int(end*1000)},volume=0.5,aformat=sample_rates=44100:channel_layouts=stereo[b1];"
for i,(f,t,v) in enumerate(EV):
  fc+=f"[{i+3}]adelay={int(t*1000)}|{int(t*1000)},volume={v},aformat=sample_rates=44100:channel_layouts=stereo[e{i}];"
fc+="[mu][b0][b1]"+''.join(f"[e{i}]" for i in range(len(EV)))+f"amix=inputs={3+len(EV)}:normalize=0,apad=whole_dur={tot},atrim=0:{tot},loudnorm=I=-14:TP=-1.5:LRA=11[o]"
run('ffmpeg','-y','-loglevel','error',*ins,'-filter_complex',fc,'-map','[o]','-ar','44100','mixn.wav')
caps=[[0.3,2.9,"Lunes. 6:00"],[3.3,5.8,"Llevo meses en piloto automático."],[10.8,12.6,"— Tenemos que hablar."],[14.0,15.6,"*PORTAZO*"],[17.4,18.9,"No estoy cansado."],[18.9,21.6,"Estoy apagado."]]
d={"plain":True,"segs":[{"type":"speak","t0":0,"t1":end},{"type":"end","t0":end,"t1":tot}],"caps":caps,"keys":[[-0.4,"LA SEMANA QUE|DEJÉ DE AGUANTAR"]],"label":"EPISODIO 1 · LUNES","endnote":"MAÑANA · EPISODIO 2","ymax":0,"steps":[],"full":[],"punch":[],"broll":[],"end":end,"tot":tot,"endq":"¿VAS EN PILOTO AUTOMÁTICO?|ESCRIBE \"SÍ\""}
open('data_seg.js','w').write('window.D='+json.dumps(d,ensure_ascii=False)+';window.ENV=[];')
print(end,tot)
