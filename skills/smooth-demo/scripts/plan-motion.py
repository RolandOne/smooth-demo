#!/usr/bin/env python3
"""Suggest editable cursor/camera keyframes from recorded action markers."""
import argparse,json,pathlib
from PIL import Image

def plan(manifest, data):
    with Image.open(manifest.parent/data['frames'][0]['file']) as first: w,h=first.size
    duration=data['duration'];events=sorted(data.get('events',[]),key=lambda e:e['time'])
    chapters=data.get('chapters',[{'name':'take','time':0,'duration':duration}])
    cur=[{'time':0,'x':w*.82,'y':h*.8,'kind':'arrow'}];clicks=[];cam=[]
    def ck(t,z=1,x=None,y=None):cam.append({'time':max(0,t),'zoom':z,'x':w/2 if x is None else x,'y':h/2 if y is None else y})
    prev=cur[0]
    for e in events:
        if e['name'].startswith('move-') and 'x' in e:
            cur.append({'time':e['time'], 'x':prev['x'],'y':prev['y'],'kind':'arrow'})
        elif e['name'].startswith('click-') and 'x' in e:
            # Text controls may supply cursor:'text'; marker-name fallback is editable.
            kind=e.get('cursor','text' if any(n in e['name'] for n in ['email','password','notes','search','input']) else 'hand')
            prev={'time':e['time'],'x':e['x'],'y':e['y'],'kind':kind};cur.append(prev);clicks.append(e)
        elif e['name'].startswith('focus-') and 'x' in e:
            cur.append({'time':e['time'],'x':prev['x'],'y':prev['y'],'kind':'arrow'})
            prev={'time':min(duration,e['time']+1.1),'x':e['x'],'y':e['y'],'kind':'arrow'};cur.append(prev)
    for ch in chapters:
        start=ch['time'];end=start+ch['duration'];es=[e for e in events if start<=e['time']<end]
        ck(start)
        cutoff=next((e['time'] for e in es if e['name']=='zoom-out'),end-1.4)
        targets=[e for e in es if e['name'].startswith(('click-','focus-')) and 'x' in e and e['time']<cutoff and not any(k in e['name'] for k in ['sign-in','submit','request','events','close-'])]
        if targets and cutoff-start>2.3:
            xs=[e['x'] for e in targets];ys=[e['y'] for e in targets];x=(min(xs)+max(xs))/2;y=(min(ys)+max(ys))/2
            if any(e['name']=='focus-outcome' for e in targets):x=w/2;y=h*.3
            boxes=[e['focusBox'] for e in targets if 'focusBox' in e]
            if boxes:x=(min(b[0] for b in boxes)+max(b[0]+b[2] for b in boxes))/2;y=(min(b[1] for b in boxes)+max(b[1]+b[3] for b in boxes))/2
            z=min(1.65,w/(max(xs)-min(xs)+440),h/(max(ys)-min(ys)+320));z=max(1,z)
            zoom_start=max(start+.2,targets[0]['time']-1.35)
            zoom_end=min(zoom_start+1.2,cutoff-.5)
            ck(zoom_start);ck(zoom_end,z,x,y);ck(cutoff,z,x,y);ck(min(end-.02,cutoff+1.2))
        ck(end-.001)
    def unique(keys):return [v for _,v in sorted({round(k['time'],4):k for k in keys}.items())]
    cur.append({'time':duration,'x':prev['x'],'y':prev['y'],'kind':prev['kind']})
    return {'capture':str(manifest),'output':'motion-demo.mp4','duration':duration,'size':[1600,1000],'fps':60,'padding':90,'label':'App demo','cursorSize':34,'cursorCurvature':.16,'camera':unique(cam),'cursor':unique(cur),'clicks':clicks}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('capture');p.add_argument('output');p.add_argument('--label',default='App demo');a=p.parse_args();m=pathlib.Path(a.capture).resolve();d=json.loads(m.read_text())
    if not d.get('frames') or d.get('status') in ['recording','interrupted','failed']:raise ValueError('Use a complete reviewed capture')
    result=plan(m,d);result['label']=a.label;out=pathlib.Path(a.output).resolve();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2));print(out)
