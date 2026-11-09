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
H=[B['01'],B['01']+11.64,B['02'],B['02']+7.92,B['02']+17.6,B['03']+6.6,B['04']+8.5,B['05']+9.9,B['06']+.6,B['06']+9.01,B['06']+21.7,B['07']+24.36,B['08']+3.04,B['08']+19.75,B['08']+22.85,B['08']+24.06,B['09']+8.13]
for h in H: big=h in (B['06']+9.01,B['08']+22.85);add(boom(2.4 if big else 1.6),h,1.0 if big else .6); add(whoosh(),h-.45,.25)
for k in ['02','03','04','05','06','07','08','09']: add(whoosh(.8),B[k]-1.0,.3)
# mezcla: música fuerte, hueco en medios bajo la voz
e=np.clip(lp(np.abs(V),5)/0.06,0,1);ek=lp(e,3)[:,None]
mid=np.stack([bp(M[:,0],1000,4000),bp(M[:,1],1000,4000)],1)
Mm=(M-0.5*mid*ek)*(1-0.22*ek)
tt=np.arange(N)/SR
musenv=np.interp(tt,[0,14.0,16.5,192.0,194.0,213],[1,1,0.06,0.06,1.6,1.6])  # música fuerte solo al principio y al final
Mm=Mm*musenv[:,None]
ir_n=int(1.4*SR);ir=rng.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR/.35);ir=lp(ir,5000);ir/=np.abs(ir).sum()**.5*10
Vr=V+fftconvolve(V,ir)[:N]*.25
st=Mm*0.62+np.stack([FX,FX],1)*0.35+np.stack([Vr,Vr],1)*0.95
fo=int(2*SR);st[-fo:]*=np.linspace(1,0,fo)[:,None]
st=np.tanh(st/np.max(np.abs(st))*1.8);st/=np.max(np.abs(st))*1.05
wavfile.write('mix_v2.wav',SR,(st*32767).astype(np.int16));print('ok')
