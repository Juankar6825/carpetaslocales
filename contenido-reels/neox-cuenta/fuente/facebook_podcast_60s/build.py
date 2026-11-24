import json,subprocess as sp,sys,os
D=os.path.dirname(os.path.abspath(__file__));os.chdir(D)
def dur(f):return float(sp.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
def run(*a):sp.run(list(a),check=True)
VF='scale=720:1280,setsar=1,fps=30'
# segmentos: (tipo, fuente, ini, fin, pausa_antes, pausa_despues)
LEAD=0.05;GAP=0.25
q1,q2,q3,q4=[dur(x) for x in['preg.wav','q2.wav','q3.wav','q4.wav']]
a3=dur('resp3.wav')
TL=[('q','preg.wav',q1,LEAD),('a','neox.wav',0.0,14.48),('q','q2.wav',q2,0.15),('a','neox.wav',14.48,23.03),
    ('q','q3.wav',q3,0.15),('a3','resp3.wav',0,a3),('q','q4.wav',q4,0.15),('a','neox.wav',23.03,34.69)]
t=0;vparts=[];aparts=[];marks=[]
for i,s in enumerate(TL):
  if s[0]=='q':
    L=s[3]+s[2]+GAP;marks.append(('q',t,t+s[3],s[1]))
    run('ffmpeg','-y','-loglevel','error','-loop','1','-t',f'{L}','-i','podcast.png','-vf',VF+',scale=720:1280','-c:v','libx264','-crf','16','-pix_fmt','yuv420p',f'pv{i}.mp4')
    run('ffmpeg','-y','-loglevel','error','-f','lavfi','-t',f'{s[3]}','-i','anullsrc=r=44100:cl=mono','-i',s[1],'-f','lavfi','-t',f'{GAP}','-i','anullsrc=r=44100:cl=mono','-filter_complex','[0][1][2]concat=n=3:v=0:a=1,aformat=sample_rates=44100:channel_layouts=mono',f'pa{i}.wav')
  else:
    src='avatar.mp4' if s[0]=='a' else 'avatar3.mp4';a0,a1=s[2],s[3];L=a1-a0;marks.append((s[0],t,a0,None))
    run('ffmpeg','-y','-loglevel','error','-ss',f'{a0}','-t',f'{L}','-i',src,'-vf',VF+',tpad=stop_mode=clone:stop_duration=1','-t',f'{L}','-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p',f'pv{i}.mp4')
    run('ffmpeg','-y','-loglevel','error','-ss',f'{a0}','-t',f'{L}','-i',s[1],'-af','aformat=sample_rates=44100:channel_layouts=mono,apad','-t',f'{L}',f'pa{i}.wav')
  L=dur(f'pa{i}.wav');marks[-1]=marks[-1]+(L,);t+=L
open('vl.txt','w').write(''.join(f"file 'pv{i}.mp4'\n" for i in range(len(TL))))
open('al.txt','w').write(''.join(f"file 'pa{i}.wav'\n" for i in range(len(TL))))
run('ffmpeg','-y','-loglevel','error','-f','concat','-i','vl.txt','-c','copy','comp.mp4')
run('ffmpeg','-y','-loglevel','error','-f','concat','-i','al.txt','voz.wav')
json.dump({'marks':marks,'end':t},open('tl.json','w'),indent=1);print(json.dumps(marks),t)
