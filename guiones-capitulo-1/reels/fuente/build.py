import json,re,subprocess,sys,os
S=os.path.dirname(os.path.abspath(__file__))+'/..'
REPO='/home/user/carpetaslocales/guiones-capitulo-1'
TEXT={
'v1':{'01':'Voy a ser brutalmente honesto contigo. Llevas años pidiendo cosas al universo. Lo escribes. Lo visualizas. Lo pegas en la nevera. ¿Y qué ha cambiado? Exacto. Hoy te cuento por qué.',
      '02':'Te han dicho que basta con desearlo con fuerza. Que lo escribas en un papel bonito. Que hagas tu tablero de visión y esperes. Si fuera tan fácil, ya lo tendrías todo. Tú y todo el mundo. La manifestación no es un juego de deseos lanzados al aire. Es un juego de poder interno. Y tiene una regla que casi nadie te explica.',
      '03':'No manifiestas lo que quieres. Manifiestas lo que toleras.'},
'v2':{'03':'Dices que quieres más dinero. Y te pasas la tarde con gente que solo habla de lo mal que está todo. Lo que escuchas cada día acaba siendo lo que crees.',
      '04':'Dices que quieres amor del bueno. Y sigues contestando a quien ya sabes cómo termina. Cada vez que contestas, le dices a la vida: "tranquila, sigo disponible para lo de siempre".',
      '05':'Dices que quieres éxito. Y el día empieza ganándote el botón de posponer. La primera decisión del día, y ya la has perdido. No es por falta de ganas. Es por falta de pruebas.'},
'v3':{'06':'Estás en modo víctima cuando te quejas en vez de actuar. Cuando crees que las circunstancias mandan. Cuando esperas a que alguien venga a salvarte. Estás en modo creador cuando tomas decisiones sin esperar permiso. Cuando cada problema es una oportunidad para demostrar quién eres. Cuando actúas, y el universo responde.',
      '07':'Si quieres ser un gran manifestador, tienes que despedirte de tu vieja versión de víctima. Esa que siempre tiene una buena excusa. Esa que te protege, sí, pero también te tiene encerrado. Solo desde tu poder interno puedes atraer una realidad poderosa. Así que hoy, antes de dormir, haz una sola cosa en modo creador. Una. La que llevas días evitando. Hoy eliges.'}}
CLIPS=[('v1','video1','video1_manifiestas_lo_que_toleras_NEOX.mp4',['01','02','03'],'LA VERDAD INCÓMODA|SOBRE LA MANIFESTACIÓN','reel1_manifiestas_lo_que_toleras.mp4'),
       ('v2','video2','video2_manifestar_es_demostrar_NEOX.mp4',['03','04','05'],'LO QUE DICES|≠ LO QUE HACES','reel2_lo_que_dices_lo_que_haces.mp4'),
       ('v3','video3','video3_victima_o_creador_NEOX.mp4',['06','07'],'¿MODO VÍCTIMA|O MODO CREADOR?','reel3_victima_o_creador.mp4')]
def sil_ends(f):
    o=subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af','silencedetect=n=-38dB:d=0.15','-f','null','-'],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',o)];en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',o)]
    return st,en
def chunks(sent,maxc=34):
    w=sent.split();out=[];cur=''
    for x in w:
        if cur and len(cur)+1+len(x)>maxc: out.append(cur);cur=x
        else: cur=(cur+' '+x).strip()
    if cur: out.append(cur)
    # evita una última línea de una sola palabra corta
    if len(out)>1 and len(out[-1])<8:
        last=out.pop(); out[-1]+=' '+last
    return out
def phrases(text,wav,t0):
    st,en=sil_ends(wav);d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',wav]))
    s0=0.0
    if st and st[0]<0.05 and en: s0=en[0]
    e0=d
    if st and st[-1]>d-1.0: e0=st[-1]
    sents=[x for x in re.split(r'(?<=[.?!…])\s+',text) if x]
    tot=sum(len(x) for x in sents);pos=0;res=[]
    starts=[]
    for x in sents:
        t=s0+(e0-s0)*pos/tot
        c=[e for e in en if abs(e-t)<0.8]
        if c and pos>0: t=min(c,key=lambda e:abs(e-t))
        starts.append(t);pos+=len(x)
    starts.append(e0)
    for i,x in enumerate(sents):
        a,b=starts[i],starts[i+1];cs=chunks(x);L=sum(len(c) for c in cs);p=0
        for c in cs:
            ca=a+(b-a)*p/L;p+=len(c);cb=a+(b-a)*p/L;res.append((t0+ca,t0+cb,c))
    return res
def ts(t):
    t=max(0,t);h=int(t//3600);m=int(t%3600//60);s=t%60;return f'{h}:{m:02d}:{s:05.2f}'
def esc(s): return s.replace('{','(').replace('}',')')
for key,folder,src,blocks,title,out in CLIPS:
    TL=json.load(open(f'{S}/{folder}/timeline.json'));B={v['b']:v for v in TL['voice']}
    a=B[blocks[0]]['t']-0.7;b=B[blocks[-1]]['t']+B[blocks[-1]]['d']+(2.4 if key=='v3' else 1.2);L=b-a;CTA=3.5;TOT=L+CTA
    caps=[]
    for k in blocks: caps+=phrases(TEXT[key][k],f'{S}/{folder}/voz/{k}.wav',B[k]['t']-a)
    t1,t2=title.split('|')
    ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Anton,112,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,6,0,8,40,40,170,1
Style: Gold,Anton,124,&H0042B9F5,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,7,0,8,40,40,300,1
Style: Cap,Anton,96,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,1,0,1,8,2,2,50,50,470,1
Style: Brand,Oswald,40,&H008AE0FF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,6,0,1,3,0,2,40,40,120,1
Style: Cta,Anton,92,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,6,0,5,40,40,0,1
Style: CtaG,Anton,110,&H0042B9F5,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,6,0,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,{ts(0)},{ts(L)},Title,,0,0,0,,{{\\fad(150,200)}}{esc(t1)}
Dialogue: 1,{ts(0.25)},{ts(L)},Gold,,0,0,0,,{{\\fad(150,200)\\t(0,300,\\fscx100\\fscy100)}}{esc(t2)}
Dialogue: 1,{ts(0)},{ts(L)},Brand,,0,0,0,,EL GRAN MANIFESTADOR · CAPÍTULO 1
"""
    for (x,y,c) in caps:
        y=min(y,L-0.05)
        if y-x<0.25: continue
        ass+=f"Dialogue: 2,{ts(x)},{ts(y)},Cap,,0,0,0,,{{\\fad(60,60)\\t(0,120,\\fscx104\\fscy104)\\t(120,220,\\fscx100\\fscy100)}}{esc(c.upper())}\n"
    ass+=f"Dialogue: 2,{ts(L)},{ts(TOT)},Cta,,0,0,0,,{{\\an7\\pos(0,0)\\fad(250,0)\\1c&H000000&\\1a&H28&\\bord0\\p1}}m 0 0 l 1080 0 1080 1920 0 1920{{\\p0}}\n"
    ass+=f"Dialogue: 3,{ts(L)},{ts(TOT)},Cta,,0,0,0,,{{\\pos(540,780)\\fad(200,0)}}MIRA EL VÍDEO COMPLETO\n"
    ass+=f"Dialogue: 3,{ts(L+0.35)},{ts(TOT)},CtaG,,0,0,0,,{{\\pos(540,930)\\fad(200,0)}}ENLACE EN LA BIO\n"
    ass+=f"Dialogue: 3,{ts(L+0.7)},{ts(TOT)},Cta,,0,0,0,,{{\\pos(540,1090)\\fad(200,0)\\fs64}}CAPÍTULO 1 · 3 VÍDEOS\n"
    open(f'{key}.ass','w').write(ass)
    vf=(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={CTA},split[s1][s2];"
        f"[s1]scale=3414:1920,crop=1080:1920,boxblur=30:3,eq=brightness=-0.28:saturation=0.8[bg];"
        f"[s2]scale=1080:608[fg];[bg][fg]overlay=0:600:shortest=1,"
        f"drawbox=x=0:y=596:w=1080:h=4:color=0xF5B942@0.9:t=fill,drawbox=x=0:y=1208:w=1080:h=4:color=0xF5B942@0.9:t=fill,"
        f"ass={key}.ass:fontsdir=fonts[v];"
        f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,apad=pad_dur={CTA}[va];"
        f"[1:a]atrim=0:{TOT},asetpts=PTS-STARTPTS,volume=0.32,afade=t=in:d=0.4,afade=t=out:st={TOT-1.8}:d=1.8[mu];"
        f"[va][mu]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1:LRA=11[a]")
    cmd=['ffmpeg','-loglevel','error','-y','-i',f'{REPO}/{folder}/{src}','-i',f'{S}/{folder}/musica_213.wav','-filter_complex',vf,'-map','[v]','-map','[a]','-t',str(TOT),'-r','30',
         '-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','44100','-movflags','+faststart',out]
    subprocess.run(cmd,check=True)
    print(out,round(TOT,1),'s',len(caps),'subtítulos')
