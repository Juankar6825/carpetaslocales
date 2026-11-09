import json,sys,numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
SR=44100;D=json.load(open('data.json'));rng=np.random.default_rng(5)
lp=lambda x,f:sosfilt(butter(2,f,'low',fs=SR,output='sos'),x);hp=lambda x,f:sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
bp=lambda x,a,b:sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
sr,mus=wavfile.read('musV2.wav');mus=mus.astype(float)/32768;mus/=np.max(np.abs(mus))
for k,d in D.items():
    N=int(d['tot']*SR);tt=np.arange(N)/SR
    s,v=wavfile.read(f'voz/{k}.wav');v=v.astype(float)/32768;v=hp(v,90);v=np.tanh(v/np.max(np.abs(v))*1.6)/np.tanh(1.6)
    V=np.zeros(N);i=int(0.35*SR);V[i:i+len(v)]=v[:N-i]
    M=mus[:N].copy()
    env=np.interp(tt,[0,0.6,d['follow'],d['follow']+.4,d['tot']-1.2,d['tot']],[0.75,0.42,0.42,0.85,0.85,0])
    e=np.clip(lp(np.abs(V),5)/0.06,0,1);ek=lp(e,3)
    mid=np.stack([bp(M[:,0],1000,4000),bp(M[:,1],1000,4000)],1)
    M=(M-0.45*mid*ek[:,None])*env[:,None]
    FX=np.zeros(N)
    def add(x,t,gn):
        j=int(t*SR);n=min(len(x),N-j);FX[j:j+n]+=x[:n]*gn
    def boom(dd=1.6):
        n=int(dd*SR);u=np.arange(n)/SR;ph=2*np.pi*np.cumsum(26+70*np.exp(-u*8))/SR
        return np.tanh(2.5*np.sin(ph)*np.exp(-u*1.6))+lp(rng.standard_normal(n),900)*np.exp(-u*12)*.5
    def whoosh(dd=.5):
        n=int(dd*SR);u=np.arange(n)/SR;return bp(rng.standard_normal(n),400,4000)*np.sin(np.pi*u/dd)**2
    for h,gn in [(0.05,.7),(d['twist'],.85),(d['follow'],.8)]:
        add(boom(),h,gn);
        if h>0.5: add(whoosh(),h-.45,.3)
    st=M*0.9+np.stack([FX,FX],1)*0.3+np.stack([V,V],1)*0.95
    st=np.tanh(st/np.max(np.abs(st))*1.6);st/=np.max(np.abs(st))*1.05
    wavfile.write(f'{k}_mix.wav',SR,(st*32767).astype(np.int16));print(k,'ok')
