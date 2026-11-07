import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=44100; DUR=37.0; N=int(SR*DUR); t=np.arange(N)/SR
rng=np.random.default_rng(3)
L=np.zeros(N); R=np.zeros(N)
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
def add(sig,start,gain=1.0,pan=0.0):
    i=int(start*SR); n=min(len(sig),N-i)
    if n<=0: return
    L[i:i+n]+=sig[:n]*gain*(1-pan)/1; R[i:i+n]+=sig[:n]*gain*(1+pan)/1
def env(n,a,d): 
    tt=np.arange(n)/SR; return np.minimum(tt/a,1)*np.exp(-tt/d)

# drone (A menor) con swells
drone=np.zeros(N)
for f,a in [(55,1),(55.4,.7),(82.4,.5),(110,.35),(130.8,.2)]:
    ph=2*np.pi*f*t
    saw=sum(np.sin(k*ph)/k for k in range(1,8))
    drone+=a*saw
drone=lp(drone,300+200*0)
lvl=np.interp(t,[0,2,13,15,31,34,37],[0,.25,.35,.5,.6,.5,0])
drone*=lvl*0.12
L+=drone; R+=np.roll(drone,300)

# tic-tac tensión 0-13
for k in np.arange(0.5,13,0.5):
    n=int(.05*SR); tick=hp(rng.standard_normal(n),3000)*env(n,.001,.012)
    add(tick,k,.18+.1*(k/13),pan=.3 if int(k*2)%2 else -.3)
# latido 10-13
for k in [10.2,10.5,11.2,11.5,12.2,12.5]:
    n=int(.4*SR); tt=np.arange(n)/SR
    add(np.sin(2*np.pi*(50+40*np.exp(-tt*30))*tt)*env(n,.003,.12),k,.9)
# pulso de bajo 17-31 (120 bpm)
for k in np.arange(17,31,0.5):
    n=int(.35*SR); tt=np.arange(n)/SR
    kick=np.sin(2*np.pi*(45+110*np.exp(-tt*35))*tt)*env(n,.002,.1)
    add(np.tanh(kick*2),k,.55)
    if (k*2)%2==1:
        hn=int(.08*SR); add(hp(rng.standard_normal(hn),6000)*env(hn,.001,.02),k,.12)

def braam(dur=2.4,base=55):
    n=int(dur*SR); tt=np.arange(n)/SR
    s=np.zeros(n)
    for f in [base,base*1.003,base*2,base*2.997,base*1.5,base*4]:
        ph=2*np.pi*f*tt
        s+=sum(np.sin(k*ph)/k for k in range(1,12))
    s=np.tanh(s*0.8)
    s=lp(s,1800)*env(n,.02,.9)
    sub=np.sin(2*np.pi*(30+60*np.exp(-tt*6))*tt)*env(n,.003,.8)*1.4
    nz=lp(rng.standard_normal(n),900)*env(n,.001,.15)*.8
    return s*.6+sub+nz
def hit(dur=1.0):
    n=int(dur*SR); tt=np.arange(n)/SR
    sub=np.sin(2*np.pi*(38+90*np.exp(-tt*18))*tt)*env(n,.002,.35)
    nz=bp(rng.standard_normal(n),80,2500)*env(n,.001,.08)
    return np.tanh((sub*1.3+nz*.7)*1.5)
def riser(dur):
    n=int(dur*SR); tt=np.arange(n)/SR; x=tt/dur
    nz=rng.standard_normal(n)
    out=np.zeros(n); seg=2048
    for i in range(0,n,seg):
        f=300+8000*x[i]**2
        out[i:i+seg]=bp(nz[i:i+seg+0],f*0.7,min(f*1.3,20000))[:len(out[i:i+seg])]
    tone=np.sin(2*np.pi*np.cumsum(200+600*x**2)/SR)*.3
    return (out+tone)*x**2
def whoosh(dur=.5):
    n=int(dur*SR); tt=np.arange(n)/SR
    return lp(rng.standard_normal(n),2500)*np.sin(np.pi*tt/dur)**2

HITS=[3.2,6.6,7.7,8.8,13.0,15.0,17.0,18.2,19.4,21.0,22.6,23.2,25.0,27.0,28.5,31.0]
BIG=[15.0,23.2,27.0,28.5,31.0]
for h in HITS:
    if h in BIG: add(braam(3.2 if h==31 else 2.2, 55 if h!=28.5 else 65.4),h,.9)
    else: add(hit(),h,.75)
    add(whoosh(),h-.35,.25)
# cristal roto 22.6
n=int(1.2*SR); add(hp(rng.standard_normal(n),2500)*env(n,.001,.25),22.6,.5,pan=.2)
for k in range(25):
    m=int(.03*SR); add(np.sin(2*np.pi*(3000+rng.random()*5000)*np.arange(m)/SR)*env(m,.001,.01),22.6+rng.random()*.9,.15,pan=rng.random()-.5)
# subidas antes de los golpes grandes
for h,d in [(15.0,2.0),(23.2,0.6),(27.0,1.8),(31.0,2.4)]:
    add(riser(d),h-d,.35)
# silencio dramático antes de 15 y 31: dip
for h in [15.0,31.0]:
    i0=int((h-.25)*SR);i1=int(h*SR); L[i0:i1]*=np.linspace(1,.2,i1-i0); R[i0:i1]*=np.linspace(1,.2,i1-i0)
# acorde final
n=int(6*SR); tt=np.arange(n)/SR; ch=np.zeros(n)
for f in [110,130.8,164.8,220,261.6,329.6]:
    ch+=np.sin(2*np.pi*f*tt+np.sin(2*np.pi*.3*tt))
ch=lp(ch,1500)*np.minimum(tt/1.5,1)*np.exp(-tt/4)*.07
add(ch,31.2,1)

# reverb
ir_n=int(2.2*SR); ir=rng.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR/0.6); ir=lp(ir,4000); ir/=np.abs(ir).sum()**.5*8
L=L+fftconvolve(L,ir)[:N]*.6; R=R+fftconvolve(R,ir[::-1].copy()*0+np.roll(ir,50))[:N]*.6
# fundido final + master
fade=np.ones(N); fo=int(1.2*SR); fade[-fo:]=np.linspace(1,0,fo)
st=np.stack([L,R],1)*fade[:,None]
st=np.tanh(st/np.max(np.abs(st))*1.6)
st=st/np.max(np.abs(st))*0.95
wavfile.write('audio.wav',SR,(st*32767).astype(np.int16))
print('ok')
