#!/usr/bin/env python3
"""Join chapter capture manifests without re-encoding; preserve timed events."""
import argparse,json,pathlib,os
p=argparse.ArgumentParser(description=__doc__);p.add_argument('output');p.add_argument('chapters',nargs='+');a=p.parse_args();out=pathlib.Path(a.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
result={'frames':[],'events':[],'chapters':[],'duration':0}
for chapter in a.chapters:
    source=pathlib.Path(chapter).resolve();d=json.loads(source.read_text());offset=result['duration']
    if d.get('status') in ['recording','failed','interrupted']:raise ValueError(f'Incomplete chapter: {source}')
    if not d['frames'] or d['duration']<=0:raise ValueError(f'Empty chapter: {source}')
    result['chapters'].append({'name':source.parent.name,'time':offset,'duration':d['duration']})
    for i,f in enumerate(d['frames']):
        result['frames'].append({'file':os.path.relpath(source.parent/f['file'],out.parent),'time':offset+(f['time'] if i else 0)})
    result['events'].extend({**e,'time':offset+e['time'],'chapter':source.parent.name} for e in d.get('events',[]))
    result['duration']+=d['duration']
out.write_text(json.dumps(result,indent=2));print(f'{len(result["chapters"])} chapters, {result["duration"]:.2f}s: {out}')
