import json,os
D=os.path.dirname(os.path.abspath(__file__));os.chdir(D)
tl=json.load(open('tl.json'));M=tl['marks'];END=tl['end']
old=[[4.51,6.77,"Porque durante años hice todo lo que me dijeron"],[6.77,8.24,"para cambiar mi vida…"],[8.24,9.92,"y no cambiaba nada."],[9.92,11.56,"Hasta que entendí una cosa:"],[11.56,13.63,"manifiestas lo que toleras."],[13.63,15.58,"El café frío que te bebes igual."],[15.58,17.31,"El sí que no querías dar."],[17.31,19.13,"El silencio con tu pareja."],[19.13,20.51,"Así que estoy grabando eso:"],[20.51,21.78,"mi día a día."],[21.78,24.27,"Lo que tolero y cómo dejo de tolerarlo."],[24.27,25.81,"Quince segundos, una enseñanza"],[25.81,27.68,"y un paso que puedes dar hoy."],[27.68,30.04,"Ahora estoy con una serie, \"Lo que toleras\"."],[30.04,30.96,"Y la primera parte"],[30.96,32.86,"funciona tan rápido que asusta."],[32.86,33.95,"Si alguna vez has sentido"],[33.95,35.21,"que pides y no te llega,"],[35.21,36.32,"búscame en TikTok:"],[36.32,38.2,"@neoxmanifestador"],[38.2,38.75,"Te espero allí."]]
a3=[[0.08,1.62,"Es el método que me cambió la vida,"],[1.92,3.38,"convertido en una experiencia."],[3.88,5.12,"No va de pedir más fuerte."],[5.56,6.58,"Va de dejar de pelearte"],[6.6,8.3,"con lo que sientes, entregarlo…"],[8.62,10.24,"y actuar desde quien quieres ser."],[10.64,11.44,"Lo estoy preparando,"],[11.64,13.32,"y en TikTok cuento cada paso."]]
QT={'preg.wav':["— NEOX, estás subiendo vídeos","a TikTok casi cada día. ¿Por qué?"],'q2.wav':["— ¿Y qué es exactamente lo que subes?"],'q3.wav':["— ¿Y qué es El Gran Manifestador?"],'q4.wav':["— ¿Y quién debería seguirte?"]}
caps=[];punch=[];boom=[]
for m in M:
  k,t0=m[0],m[1];L=m[-1]
  if k=='q':
    s=m[2];txt=QT[m[3]];n=len(txt);d=(L-0.25-(s-t0))/n
    for j,x in enumerate(txt):caps.append([round(s+j*d,3),round(s+(j+1)*d if j<n-1 else t0+L,3),x])
    punch.append(round(t0,3));boom.append(round(t0,3))
  elif k=='a':
    a0=m[2]
    for c0,c1,x in old:
      n0=c0-4.461;n1=c1-4.461
      if n0>=a0-0.02 and n0<a0+L-0.1:caps.append([round(t0+max(0,n0-a0),3),round(min(t0+L,t0+n1-a0),3),x])
  else:
    for c0,c1,x in a3:caps.append([round(t0+c0,3),round(t0+c1,3),x])
caps.sort()
for i in range(len(caps)-1):caps[i][1]=max(caps[i][1],min(caps[i+1][0],caps[i][1]+0.4))
E2=round(END,3);TOT=round(END+2.8,3)
d={"segs":[{"type":"speak","t0":0,"t1":E2},{"type":"end","t0":E2,"t1":TOT}],"caps":caps,"keys":[[-0.4,"POR QUÉ ESTOY|EN TIKTOK"]],"label":"ENTREVISTA A NEOX","endq":"BÚSCAME EN TIKTOK|@NEOXMANIFESTADOR","ymax":300,"steps":[],"full":[],"punch":punch,"broll":[],"end":E2,"tot":TOT}
open('data_seg.js','w').write('window.D='+json.dumps(d,ensure_ascii=False)+';window.ENV=[];')
json.dump({'boom':boom,'end':E2,'tot':TOT},open('mix.json','w'))
for c in caps:print(c)
print(punch,E2,TOT)
