#!/usr/bin/env python3
"""Render real captured frames/video with editable cursor and camera keyframes."""
import argparse,bisect,json,math,pathlib,platform,subprocess
from PIL import Image,ImageDraw,ImageFilter,ImageFont,ImageOps

def background_path(cfg, root):
    """Explicit image wins; otherwise choose an offline preset for the render host."""
    if cfg.get('background'):
        return root / cfg['background']
    preset = cfg.get('backgroundPreset', 'auto')
    if preset == 'auto':
        preset = {'Darwin': 'macos', 'Windows': 'windows'}.get(platform.system(), 'gradient')
    names = {'macos': 'lake-tahoe-day.jpg', 'windows': 'windows-11-bloom.jpg'}
    if preset == 'gradient':
        return None
    if preset not in names:
        raise ValueError('backgroundPreset must be auto, macos, windows, or gradient')
    return pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'backgrounds' / names[preset]

def ease(v):
    v=max(0,min(1,v));return v*v*v*(v*(v*6-15)+10)
def tween(t,keys,fields):
    if t<=keys[0]['time']:return tuple(keys[0][f] for f in fields)
    for a,b in zip(keys,keys[1:]):
        if t<=b['time']:
            q=ease((t-a['time'])/(b['time']-a['time']))
            return tuple(a[f]+(b[f]-a[f])*q for f in fields)
    return tuple(keys[-1][f] for f in fields)
def cursor_at(t, keys, curvature):
    if t <= keys[0]['time']:return keys[0]['x'],keys[0]['y'],keys[0].get('kind','arrow')
    for a,b in zip(keys,keys[1:]):
        if t < b['time']:
            q=ease((t-a['time'])/(b['time']-a['time']));dx=b['x']-a['x'];dy=b['y']-a['y'];dist=math.hypot(dx,dy)
            bend=min(70,dist*curvature)*4*q*(1-q)
            return a['x']+dx*q-(dy/dist*bend if dist else 0),a['y']+dy*q+(dx/dist*bend if dist else 0),('arrow' if dist>1 else a.get('kind','arrow'))
    return keys[-1]['x'],keys[-1]['y'],keys[-1].get('kind','arrow')

def cursor_sprites(size):
    sprites={}
    for kind in ['arrow','hand','text']:
        im=Image.new('RGBA',(128,160));d=ImageDraw.Draw(im)
        if kind=='arrow':
            d.polygon([(10,6),(10,114),(37,88),(57,137),(77,128),(57,82),(95,82)],fill='#16171b',outline='white',width=6);hot=(2,2)
        elif kind=='text':
            for width,color in [(15,'white'),(7,'#16171b')]:
                d.line([(52,10),(52,135)],fill=color,width=width);d.line([(31,10),(73,10)],fill=color,width=width);d.line([(31,135),(73,135)],fill=color,width=width)
            hot=(13,18)
        else:
            d.polygon([(46,10),(57,10),(60,67),(69,49),(80,50),(84,62),(93,57),(105,62),(108,99),(95,135),(49,135),(29,105),(16,86),(18,76),(28,72),(43,88),(43,18)],fill='white',outline='#16171b',width=6);hot=(13,3)
        target=(size,round(size*1.25));sprites[kind]=(im.resize(target,Image.Resampling.LANCZOS),(hot[0]*size/32,hot[1]*size/32))
    return sprites

def check_keys(keys,fields):
    if not keys:raise ValueError('Empty motion keyframes')
    last=-1
    for key in keys:
        if not math.isfinite(key['time']) or key['time']<0 or key['time']<=last:raise ValueError('Keyframe times must strictly increase')
        last=key['time']
        for f in fields:
            if not math.isfinite(key[f]):raise ValueError('Nonfinite keyframe')
        if 'zoom' in key and key['zoom']<1:raise ValueError('Zoom must be >= 1')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('config');ap.add_argument('--preview',action='store_true',help='Half-size 24fps draft, separate output');args=ap.parse_args()
    cfgpath=pathlib.Path(args.config).resolve();cfg=json.loads(cfgpath.read_text());root=cfgpath.parent
    W,H=cfg.get('size',[1600,1000]);FPS=cfg.get('fps',60)
    if args.preview:
        W=max(2,W//4*2);H=max(2,H//4*2);FPS=24;cfg['padding']=cfg.get('padding',90)/2;cfg['cursorSize']=round(cfg.get('cursorSize',32)/2);cfg['preset']='ultrafast';cfg['output']=str(pathlib.Path(cfg.get('output','motion-demo.mp4')).with_suffix(''))+'-preview.mp4'
    if min(W,H,FPS)<=0 or W%2 or H%2:raise ValueError('Positive even output dimensions required')
    output_height=H
    subtitles=cfg.get('subtitles',[])
    footer=round(H*.14) if subtitles else 0
    H-=footer
    caption_font_size=max(12,round(W*.0175))
    try:caption_font=ImageFont.truetype(cfg.get('captionFont','/System/Library/Fonts/SFNS.ttf'),caption_font_size)
    except OSError:caption_font=ImageFont.truetype('DejaVuSans.ttf',caption_font_size)
    caption_lines=[]
    measure=ImageDraw.Draw(Image.new('RGB',(1,1)))
    previous_end=0
    for cue in subtitles:
        start,end=cue['start'],cue['end']
        if not all(math.isfinite(v) for v in [start,end]) or start<previous_end or end<=start or end>cfg['duration']:
            raise ValueError('Subtitle cues must be ordered, non-overlapping, and inside the video duration')
        previous_end=end
        lines=[];line=''
        for word in cue['text'].split():
            if measure.textlength(word,font=caption_font)>W*.9:raise ValueError('Subtitle word too wide')
            candidate=(line+' '+word).strip()
            if measure.textlength(candidate,font=caption_font)>W*.9:lines.append(line);line=word
            else:line=candidate
        if line:lines.append(line)
        if not lines or len(lines)>2:raise ValueError('Keep each subtitle cue to one or two short lines')
        caption_lines.append((start,end,lines))
    duration=cfg['duration'];out=root/cfg.get('output','motion-demo.mp4')
    if duration<=0:raise ValueError('Positive duration required')
    decoder=None
    if 'video' in cfg:
        video=root/cfg['video'];info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(video)]))['streams'][0]
        iw,ih=info['width'],info['height'];decoder=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-vf',f'fps={FPS}','-frames:v',str(round(duration*FPS)),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    else:
        manifest=root/cfg['capture'];cap=json.loads(manifest.read_text());frames=cap['frames'];times=[f['time'] for f in frames]
        if not frames or times!=sorted(times):raise ValueError('Missing or unsorted captured frames')
        iw,ih=Image.open(manifest.parent/frames[0]['file']).size
    camera=cfg.get('camera',[{'time':0,'zoom':1,'x':iw/2,'y':ih/2}]);cursor=cfg.get('cursor',[{'time':0,'x':iw*.8,'y':ih*.8}])
    check_keys(camera,['zoom','x','y']);check_keys(cursor,['x','y'])
    if any(k.get('kind','arrow') not in ['arrow','hand','text'] for k in cursor):raise ValueError('Unknown cursor kind')
    pad=cfg.get('padding',90);bar=32;scale=min((W-2*pad)/iw,(H-2*pad-bar)/ih);sw,sh=round(iw*scale),round(ih*scale);X=(W-sw)//2;Y=(H-sh-bar)//2
    if min(sw,sh)<=0:raise ValueError('Padding leaves no space for recording')
    bg=Image.new('RGB',(400,250));px=bg.load()
    for y in range(250):
        for x in range(400):
            u=x/400;v=y/250;a=math.exp(-((u-.15)**2+(v-.8)**2)/.17);b=math.exp(-((u-.9)**2+(v-.12)**2)/.24);q=.5+.5*math.sin(10*u+5*v+2*math.sin(v*4))
            px[x,y]=(int(22+55*a+50*b+15*q),int(24+28*a+18*b+10*q),int(55+52*a+58*b+20*q))
    bg=bg.resize((W,H),Image.Resampling.BICUBIC).convert('RGBA')
    wallpaper=background_path(cfg,root)
    if wallpaper:
        with Image.open(wallpaper) as im:
            bg=ImageOps.fit(im.convert('RGBA'),(W,H),method=Image.Resampling.LANCZOS)
    shadow=Image.new('RGBA',(W,H));ImageDraw.Draw(shadow).rounded_rectangle((X-2,Y,X+sw+2,Y+sh+bar+12),radius=20,fill=(0,0,0,160));bg=Image.alpha_composite(bg,shadow.filter(ImageFilter.GaussianBlur(22))).convert('RGB')
    mask=Image.new('L',(sw,sh+bar));ImageDraw.Draw(mask).rounded_rectangle((0,0,sw-1,sh+bar-1),radius=14,fill=255)
    try:font=ImageFont.truetype(cfg.get('font','/System/Library/Fonts/SFNS.ttf'),13)
    except OSError:font=ImageFont.load_default()
    sprites=cursor_sprites(cfg.get('cursorSize',32))
    out.parent.mkdir(parents=True,exist_ok=True)
    enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{output_height}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset',cfg.get('preset','fast'),'-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
    last_idx=-1;source=None;base=None
    try:
        for i in range(round(duration*FPS)):
            t=i/FPS
            if decoder:
                needed=iw*ih*3;data=bytearray()
                while len(data)<needed:
                    chunk=decoder.stdout.read(needed-len(data))
                    if not chunk:break
                    data.extend(chunk)
                if len(data)==needed:source=Image.frombytes('RGB',(iw,ih),bytes(data));idx=i
                elif not data and source is not None:idx=last_idx
                else:raise ValueError('Incomplete video frame')
            else:
                idx=max(0,bisect.bisect_right(times,t)-1)
                if idx!=last_idx:source=Image.open(manifest.parent/frames[idx]['file']).convert('RGB')
            if idx!=last_idx:
                source=source.copy()
                for rect in cfg.get('redactions',[]):
                    fill=source.getpixel(tuple(rect['sample'])) if 'sample' in rect else rect.get('fill','#f9fafb')
                    ImageDraw.Draw(source).rectangle(rect['box'],fill=fill)
                panel=Image.new('RGB',(sw,sh+bar),'#303138');panel.paste(source.resize((sw,sh),Image.Resampling.LANCZOS),(0,bar));dr=ImageDraw.Draw(panel)
                for j,c in enumerate(['#ff6058','#ffbd2e','#28ca42']):dr.ellipse((15+j*19,11,25+j*19,21),fill=c)
                label=cfg.get('label','App demo');bounds=dr.textbbox((0,0),label,font=font);dr.text(((sw-(bounds[2]-bounds[0]))/2,8),label,font=font,fill='#c7cad2')
                base=bg.copy();base.paste(panel,(X,Y),mask);last_idx=idx
            z,cx,cy=tween(t,camera,['zoom','x','y']);cx=X+cx*scale;cy=Y+bar/2+cy*scale
            if z==1:cx=W/2;cy=H/2
            # Keep the camera inside the canvas during every transition.
            cx=max(W/(2*z),min(W-W/(2*z),cx));cy=max(H/(2*z),min(H-H/(2*z),cy))
            result=base.copy() if z==1 else base.transform((W,H),Image.Transform.AFFINE,(1/z,0,cx-W/(2*z),0,1/z,cy-H/(2*z)),Image.Resampling.BICUBIC)
            ux,uy,kind=cursor_at(t,cursor,cfg.get('cursorCurvature',.16));ux=(X+ux*scale-cx)*z+W/2;uy=(Y+bar+uy*scale-cy)*z+H/2
            for click in cfg.get('clicks',[]):
                dt=t-click['time']
                if 0<=dt<.6:
                    qx=(X+click['x']*scale-cx)*z+W/2;qy=(Y+bar+click['y']*scale-cy)*z+H/2
                    layer=Image.new('RGBA',(W,H));r=8+30*ease(dt/.6);ImageDraw.Draw(layer).ellipse((qx-r,qy-r,qx+r,qy+r),outline=(115,150,255,int(190*(1-dt/.6))),width=3);result=Image.alpha_composite(result.convert('RGBA'),layer).convert('RGB')
            cs,hot=sprites[kind];result.paste(cs,(round(ux-hot[0]),round(uy-hot[1])),cs)
            if footer:
                composed=Image.new('RGB',(W,output_height),'#151a23');composed.paste(result,(0,0))
                for start,end,lines in caption_lines:
                    if start<=t<end:
                        draw=ImageDraw.Draw(composed);line_height=round(caption_font_size*1.4)
                        y=H+(footer-len(lines)*line_height)//2
                        for line in lines:
                            draw.text((W/2,y),line,font=caption_font,fill='white',anchor='mt');y+=line_height
                        break
                result=composed
            enc.stdin.write(result.tobytes())
            if i% (FPS*10)==0:print(f'{t:.0f}/{duration:.0f}s',flush=True)
        enc.stdin.close()
        if enc.wait()!=0:raise RuntimeError('FFmpeg failed')
    finally:
        if decoder:
            decoder.stdout.close();decoder.terminate();decoder.wait()
        if enc.poll() is None:enc.terminate();enc.wait()
    print(out)
if __name__=='__main__':main()
