"""Approximate Rockbox renderer for the JGUlmiz WPS/SBS, used to preview layouts.
Text is rendered like convttf does it: FT char size = N pt @ 60 dpi, top-aligned in the viewport,
baseline at viewport_y + font ascent, clipped to the viewport."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np, struct
F='/home/user/scratch/'
def hexc(h): return tuple(int(h[i:i+2],16) for i in (0,2,4))
class RBFont:
    def __init__(s,px,weight,fnt):
        s.f=ImageFont.truetype(F+f'Ubuntu-{weight}.ttf',px*60/72)
        d=open(fnt,'rb').read(); s.height,s.ascent=struct.unpack('<HH',d[6:10])
def text(im,vp,s,font,col,align='c',bg=None):
    x,y,w,h=vp
    layer=Image.new('RGBA',(w,max(h,font.height)),(0,0,0,0)); d=ImageDraw.Draw(layer)
    tw=d.textlength(s,font=font.f)
    if tw>w: align='l'   # too long -> rockbox scrolls, starting left-aligned
    tx={'l':0,'c':(w-tw)//2,'r':w-tw}[align]
    d.text((tx,font.ascent),s,font=font.f,fill=hexc(col)+(255,),anchor='ls')
    layer=layer.crop((0,0,w,h))           # clip to viewport
    im.paste(layer,(x,y),layer)
def mono(im,path,x,y,frame,nframes,col,clip=None):
    b=Image.open(path).convert('L'); fh=b.height//nframes
    fr=b.crop((0,frame*fh,b.width,(frame+1)*fh))
    if clip: fr=fr.crop((0,0,min(clip[0],fr.width),min(clip[1],fr.height)))
    m=fr.point(lambda v:255 if v<128 else 0); im.paste(Image.new('RGB',fr.size,hexc(col)),(x,y),m)
def keyed(im,path,x,y,frame,nframes):
    b=Image.open(path).convert('RGB'); fh=b.height//nframes
    fr=b.crop((0,frame*fh,b.width,(frame+1)*fh)); a=np.array(fr)
    m=Image.fromarray((~np.all(a==[255,0,255],axis=-1)).astype(np.uint8)*255); im.paste(fr,(x,y),m)
def fake_art(size):
    w,h=size; yy,xx=np.mgrid[0:h,0:w]; a=np.zeros((h,w,3),np.uint8)
    a[...,0]=40+xx*150//w; a[...,1]=40+yy*80//h; a[...,2]=70
    im=Image.fromarray(a); d=ImageDraw.Draw(im)
    d.ellipse((w*.3,h*.25,w*.7,h*.65),fill=(230,200,170)); d.rectangle((w*.2,h*.7,w*.8,h),fill=(20,20,30))
    return im

def render_wps(L, root, sample):
    R=root; im=Image.open(R+'wps/JGUlmiz/wps_bg.bmp').convert('RGB')
    im.paste(Image.open(R+'wps/JGUlmiz/aa_shadow.bmp').convert('RGB'),L['shadow'])
    ax,ay,aw,ah=L['art']; s=min(aw,ah); im.paste(fake_art((s,s)),(ax+(aw-s)//2,ay+(ah-s)//2))
    f=L['fonts']
    mono(im,R+'wps/JGUlmiz/speaker.bmp',*L['spk'][:2],9,15,'cccccc',clip=L['spk'][2:])
    text(im,L['vol'],sample['vol'],f[8],'cccccc','l')
    text(im,L['clock'],sample['clock'],f[8],'cccccc','c')
    text(im,L['batt'],sample['batt'],f[8],'cccccc','r')
    bx,by,bw,bh=L['batticon']; d=ImageDraw.Draw(im); n=L['nub']
    d.rectangle((bx+n[0],by+n[1],bx+n[0]+n[2]-1,by+n[1]+n[3]-1),fill=hexc('cccccc'))
    d.rectangle((bx,by+n[4],bx+bw-1,by+bh-1),fill=hexc('cccccc'))
    for k,col in [('album','cccccc'),('year','1a1410')]: text(im,L[k],sample[k],f[8],col)
    text(im,L['artist'],sample['artist'],f[3],'f2f2f2'); text(im,L['title'],sample['title'],f[4],'222222')
    px,py,pw,ph=L['pb']; d.rectangle((px,py,px+pw-1,py+ph-1),outline=hexc('ff9500'))
    d.rectangle((px+2,py+2,px+2+int((pw-4)*0.38),py+ph-3),fill=hexc('ff9500'))
    text(im,L['el'],sample['el'],f[8],'cccccc','l'); text(im,L['tot'],sample['tot'],f[8],'cccccc','r')
    text(im,L['pos'],sample['pos'],f[8],'dddddd','c')
    mono(im,R+'wps/JGUlmiz/shuffle.bmp',*L['shuf'],0,1,'ff9500')
    keyed(im,R+'wps/JGUlmiz/play.bmp',*L['play'],1,3)
    mono(im,R+'wps/JGUlmiz/repeat.bmp',*L['rep'],1,4,'ff9500')
    return im

def render_sbs(L, root, sample, iconfile):
    R=root; im=Image.open(R+'wps/JGUlmiz/sbs_bg.bmp').convert('RGB'); f=L['fonts']; d=ImageDraw.Draw(im)
    mono(im,R+'wps/JGUlmiz/speaker.bmp',*L['spk'][:2],10,15,'cccccc',clip=L['spk'][2:])
    text(im,L['vol'],sample['vol'],f[8],'cccccc','l'); text(im,L['clock'],sample['clock'],f[8],'cccccc','c')
    text(im,L['batt'],sample['batt'],f[8],'cccccc','r')
    bx,by,bw,bh=L['batticon']; n=L['nub']
    d.rectangle((bx+n[0],by+n[1],bx+n[0]+n[2]-1,by+n[1]+n[3]-1),fill=hexc('cccccc')); d.rectangle((bx,by+n[4],bx+bw-1,by+bh-1),fill=hexc('cccccc'))
    tx,ty,tw,th=L['ticon']; mono(im,R+'wps/JGUlmiz/'+iconfile,tx,ty,1,32,'ff9500',clip=(tw,th))
    text(im,L['ttext'],'Files',f[4],'ff9500','l')
    vx,vy,vw,vh=L['vi']; lh=L['lineh']; sbw=L['sbw']; icw,ich=L['icon']
    items=['Albums','Artists','Music','Playlists','Recent Bookmarks','Settings','System']
    icons=[1,3,0,2,15,19,28]
    for i,t in enumerate(items):
        y=vy+i*lh
        if y+lh>vy+vh: break
        sel=(i==2); col='222222' if sel else 'cccccc'
        if sel: d.rectangle((vx,y,vx+vw-sbw-1,y+lh-1),fill=hexc('e7ad8e'))
        mono(im,R+'icons/ulmiz_icons.bmp',vx+2,y+(lh-ich)//2,icons[i],32,col)
        fy=y+(lh-f['ui'].height)//2
        text(im,(vx+2+icw+4,fy,vw-sbw-icw-6,f['ui'].height),t,f['ui'],col,'l')
    d.rectangle((vx+vw-sbw,vy,vx+vw-1,vy+vh-1),fill=hexc('555555')); d.rectangle((vx+vw-sbw,vy,vx+vw-1,vy+vh//3),fill=hexc('cccccc'))
    return im
