import json,subprocess
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
# (bloque, pausa antes en s)
PLAN=[('01',3.0),('02',2.2),('03',4.0),('04',3.2),('05',1.8),('06',1.8),('07',1.8),('08',4.0),('09',2.5),('10',9.0)]
t=0;V=[]
for b,gap in PLAN:
    t+=gap; d=dur(f'voz/{b}.wav'); V.append({'b':b,'t':round(t,3),'d':round(d,3)}); t+=d
TOT=213.0
print('voz termina en',round(t,2),'-> cierre',round(TOT-t,2),'s')
json.dump({'tot':TOT,'voice':V},open('timeline.json','w'),indent=1)
