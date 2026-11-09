import json,numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt,fftconvolve
SR=44100;TL=json.load(open('timeline.json'));N=int(213*SR);rng=np.random.default_rng(1)
lp=lambda x,f:sosfilt(butter(2,f,'low',fs=SR,output='sos'),x);hp=lambda x,f:sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
bp=lambda x,a,b:sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
B={v['b']:v['t'] for v in TL['voice']}
V=np.zeros(N)
for v in TL['voice']:
    s,x=wavfile.read(f"voz/{v['b']}.wav");x=x.astype(float)/32768;x=hp(x,90);x=np.tanh(x/np.max(np.abs(x))*1.6)/np.tanh(1.6)
    i=int(v['t']*SR);V[i:i+len(x)]+=x[:N-i]
s,m=wavfile.read('musica_213.wav');m=m.astype(float)/32768;M=np.zeros((N,2));M[:min(N,len(m))]=m[:N];M/=np.max(np.abs(M))
# golpes
FX=np.zeros(N)
def add(x,t,gn):
    i=int(t*SR);n=min(len(x),N-i);FX[i:i+n]+=x[:n]*gn
def boom(d=1.8):
    n=int(d*SR);tt=np.arange(n)/SR;ph=2*np.pi*np.cumsum(26+70*np.exp(-tt*8))/SR
    return np.tanh(2.5*np.sin(ph)*np.exp(-tt*1.4))+lp(rng.standard_normal(n),900)*np.exp(-tt*12)*.5
def whoosh(d=.5):
    n=int(d*SR);tt=np.arange(n)/SR;return bp(rng.standard_normal(n),400,4000)*np.sin(np.pi*tt/d)**2
H=[B['01']+9.3,B['02']+16.45,B['03']+2.05,B['04']+7.07,B['05']+6.12,B['06']+10.67,B['07']+10.28,B['08']+5.78,B['08']+27.09,B['10']+6.31]
for h in H: add(boom(2.4 if h==B['03']+2.05 else 1.6),h,1.0 if h==B['03']+2.05 else .6); add(whoosh(),h-.45,.25)
for k in ['02','03','04','05','06','07','08','09','10']: add(whoosh(.8),B[k]-1.0,.3)
# mezcla: música fuerte, hueco en medios bajo la voz
e=np.clip(lp(np.abs(V),5)/0.06,0,1);ek=lp(e,3)[:,None]
mid=np.stack([bp(M[:,0],1000,4000),bp(M[:,1],1000,4000)],1)
Mm=(M-0.5*mid*ek)*(1-0.22*ek)
tt=np.arange(N)/SR
musenv=np.interp(tt,[0,14.0,16.5,197.5,199.5,213],[1,1,0.06,0.06,1.6,1.6])  # música fuerte solo al principio y al final
Mm=Mm*musenv[:,None]
ir_n=int(1.4*SR);ir=rng.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR/.35);ir=lp(ir,5000);ir/=np.abs(ir).sum()**.5*10
Vr=V+fftconvolve(V,ir)[:N]*.25
st=Mm*0.62+np.stack([FX,FX],1)*0.35+np.stack([Vr,Vr],1)*0.95
fo=int(2*SR);st[-fo:]*=np.linspace(1,0,fo)[:,None]
st=np.tanh(st/np.max(np.abs(st))*1.8);st/=np.max(np.abs(st))*1.05
wavfile.write('mix_v1.wav',SR,(st*32767).astype(np.int16));print('ok')
