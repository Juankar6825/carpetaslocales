import json,subprocess
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
# escenas: (inicio_orig, fin_orig, fundido, [ (clip, [(offset_en_clip, t_orig), ...]) ])
SC=[
 (0.0, 3.2, .25,[('01',[(0,0.25)])]),
 (3.2, 6.6, .2, [('02',[(0,3.3)])]),
 (6.6,10.0, .3, [('03',[(0,6.7),(1.895,7.4),(3.72,8.5),(5.32,9.35)])]),
 (10.0,13.0,.2, [('04',[(0,10.2),(1.89,11.3)])]),
 (13.0,17.0,.2, [('05a',[(0,13.0)]),('05b',[(0,15.0)])]),
 (17.0,21.0,.2, [('06',[(0,17.0),(1.77,18.2),(3.47,19.4)])]),
 (21.0,25.0,.2, [('07',[(0,21.0),(2.4,21.7),(3.73,23.2)])]),
 (25.0,28.5,.15,[('08',[(0,25.0),(2.44,27.0)])]),
 (28.5,31.0,.12,[('09',[(0.05,28.5),(0.48,28.75)])]),
 (31.0,37.0,.8, [('10',[(0,31.0),(1.88,31.9),(3.14,33.6)])]),
]
K=[(0.0,0.0)]; voices=[]
for S0,S1,fade,clips in SC:
    end_prev=K[-1][0]
    for name,anch in clips:
        d=dur(f'voz/{name}.mp3')
        ln,lo=K[-1]
        vs=max(ln+(o-lo)-off for off,o in anch)
        vs=max(vs,end_prev+0.25 if voices and voices[-1][0]!=name else vs)
        for off,o in anch:
            n=vs+off
            if o>K[-1][1]+1e-6: K.append((max(n,K[-1][0]+0.001),o))
        voices.append((name,vs)); end_prev=vs+d
    tail=1.4 if S1==37.0 else 0.45
    ln,lo=K[-1]
    hold_n=max(end_prev+tail-fade, ln+(S1-fade-lo))
    K.append((hold_n,S1-fade)); K.append((hold_n+fade,S1))
TOT=K[-1][0]
def M(T):  # tiempo nuevo -> tiempo de escena (avanza a ritmo 1 y luego espera)
    for (n0,o0),(n1,o1) in zip(K,K[1:]):
        if T<=n1:
            if n1-n0>=o1-o0: return min(o0+(T-n0),o1)
            return o0+(T-n0)*(o1-o0)/(n1-n0)
    return K[-1][1]
def Minv(o):
    for (n0,o0),(n1,o1) in zip(K,K[1:]):
        if o<=o1:
            if n1-n0>=o1-o0: return n0+(o-o0)
            return n0+(o-o0)*(n1-n0)/(o1-o0)
    return TOT
fps=30;N=int(round(TOT*fps))
json.dump({'tot':TOT,'frames':[M(i/fps) for i in range(N)]},open('framemap.json','w'))
json.dump({'tot':TOT,'K':K,'voices':voices},open('timeline.json','w'),indent=1)
print('duración',round(TOT,2),'s');[print(v) for v in voices]
