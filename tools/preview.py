import sys; sys.path.insert(0,'/home/user/port'); sys.path.insert(0,'/home/user/port/v2')
from render import RBFont, text, mono, hexc
from design import L, ACCENT, TEXT_HEX as T
from PIL import Image, ImageDraw
R='/home/user/UImiz-Revamped-AP80ProMax/.rockbox/'; D=R+'wps/UImiz Revamped/'
f8=RBFont(27,'Regular',R+'fonts/27-Ubuntu-Regular.fnt'); f7=RBFont(34,'Bold',R+'fonts/34-Ubuntu-Bold.fnt')
f4=RBFont(38,'Medium',R+'fonts/38-Ubuntu-Medium.fnt'); f5=RBFont(16,'Medium',R+'fonts/16-Ubuntu-Medium.fnt')
def vp(s): return tuple(int(v) for v in s.split(','))
wps=open(R+'wps/UImiz Revamped.wps').read()
import re
def V(prefix):  # find viewport rect following a comment
    i=wps.index(prefix); m=re.search(r'%V\((\d+),(\d+),(\d+),(\d+)',wps[i:]); return tuple(map(int,m.groups()))
def frame(img,file,box,idx,n):
    b=Image.open(D+file); h=b.height//n; img.paste(b.crop((0,idx*h,b.width,(idx+1)*h)),box[:2])
def render(art, s, play_state=2, shuf=1, rep=0):
    im=Image.open(D+'wps_bg.bmp').convert('RGB')
    ax,ay,aw,ah=L['art']
    if art is not None:
        a=art.copy(); a.thumbnail((aw,ah),Image.LANCZOS); im.paste(a,(ax+(aw-a.width)//2,ay+(ah-a.height)//2))
    d=ImageDraw.Draw(im)
    text(im,V('# Album'),s['album'],f8,T['album']); text(im,V('# Year'),s['year'],f8,T['year'])
    text(im,V('# Artist'),s['artist'],f7,T['artist']); text(im,V('# Title'),s['title'],f4,T['title'])
    x0,y0,x1,y1=L['track']; d.rectangle((x0,y0,x1-1,y1-1),outline=ACCENT)
    d.rectangle((x0+1,y0+1,x0+1+int((x1-x0-2)*s['prog']),y1-2),fill=ACCENT)
    text(im,V('# Time elapsed'),s['el'],f8,T['status'],'l'); text(im,V('# Time total'),s['tot'],f8,T['status'],'r')
    text(im,V('# Playlist position'),s['pos'],f8,T['status'],'c')
    frame(im,'shuffle.bmp',L['shuffle'],shuf,2); frame(im,'play.bmp',L['play'],play_state,3); frame(im,'repeat.bmp',L['repeat'],rep,5)
    return im
ref=Image.open('/home/user/uploads/wps-wps.png').convert('RGB')
art=Image.open('/home/user/scratch/summernights.jpg').convert('RGB')  # Maverick Soul - Summer Nights (Only Good Vibes, Bandcamp cover)
s=dict(vint='-3',vdec='.5',clock='21:36',batt='78%',album='Only Good Vibes',year='2017',artist='Maverick Soul',title='Summer Nights',prog=0.4,el='1:38',tot='4:05',pos='1 of 1')
a=render(art,s)
s2=dict(vint='-48',vdec='.0',clock='21:29',batt='83%',album='When The City Sleeps',year='2026',artist='Alex Isley',title='Moonlight On Vermont',prog=0.21,el='1:02',tot='4:53',pos='4 sur 14')
import numpy as np
yy,xx=np.mgrid[0:300,0:300]; g=np.zeros((300,300,3),np.uint8); g[...,0]=30+xx//6; g[...,1]=40+yy//8; g[...,2]=150+xx//4
b=render(Image.fromarray(g),s2,play_state=1,shuf=0,rep=2)
a.save('/home/user/scratch/v2_a.png'); b.save('/home/user/scratch/v2_b.png')
refs=ref.resize((384,640),Image.LANCZOS)
c=Image.new('RGB',(384+360*2+40,640),(255,255,255)); c.paste(refs,(0,0)); c.paste(a,(404,0)); c.paste(b,(784,0)); c.save('/home/user/scratch/v2_compare.png')

# ---------------- menu (SBS + list)
f3=RBFont(34,'Medium',R+'fonts/34-Ubuntu-Medium.fnt')
from design import ACCENT_HEX
sb=Image.open(D+'sbs_bg.bmp').convert('RGB'); d=ImageDraw.Draw(sb)
text(sb,(24,8,48,26),'-3',f8,T['status'],'r'); text(sb,(74,0,30,16),'.5',f5,T['status'],'l'); text(sb,(74,16,30,16),'dB',f5,T['status'],'l')
text(sb,(120,8,120,27),'21:36',f8,T['status'],'c'); text(sb,(254,8,78,26),'78%',f8,T['status'],'r')
bx,by=337,10; d.rectangle((bx+3,by+1,bx+7,by+2),fill=hexc(T['status'])); d.rectangle((bx,by+3,bx+10,by+21),fill=hexc(T['status']))
mono(sb,D+'title_icons.bmp',5,61,31,32,ACCENT_HEX,clip=(30,38))  # main menu = home icon (last frame), drawn at the viewport origin like Rockbox
text(sb,(41,53,297,38),'Main Menu',f4,ACCENT_HEX,'l')
vx,vy,vw,vh,lh,sbw=15,98,334,465,66,30
items=['Music','Files','Playlists','Now Playing','Recent Bookmarks','Settings','System']; icons=[0,1,2,3,15,19,28]
for i,t in enumerate(items):
    y=vy+i*lh; sel=(i==0); col='1e1626' if sel else T['status']
    if sel: d.rectangle((vx,y,vx+vw-sbw-1,y+lh-1),fill=ACCENT)
    mono(sb,R+'icons/UImiz Revamped icons.bmp',vx+2,y+(lh-24)//2,icons[i],32,col)
    text(sb,(vx+44,y+(lh-33)//2,vw-sbw-46,33),t,f3,col,'l')
d.rectangle((vx+vw-sbw,vy,vx+vw-1,vy+vh-1),outline=hexc(T['status'])); d.rectangle((vx+vw-sbw+2,vy+2,vx+vw-3,vy+vh//2),fill=hexc(T['status']))
sb.save('/home/user/scratch/v3_menu.png')
c=Image.new('RGB',(360*3+40,640),(255,255,255)); c.paste(a,(0,0)); c.paste(b,(380,0)); c.paste(sb,(760,0)); c.save('/home/user/scratch/v3_all.png')

# ---------------- USB screen
f56=RBFont(56,'Medium',R+'fonts/56-Ubuntu-Medium.fnt'); f20=RBFont(20,'Medium',R+'fonts/20-Ubuntu-Medium.fnt')
u=Image.open(D+'sbs_bg.bmp').convert('RGB'); u.paste(Image.open(D+'usb_screen.bmp'),(0,42)); d=ImageDraw.Draw(u)
def status_bar(im, batt, charging, peak=None, bgfile='wps_bg.bmp'):
    im.paste(Image.open(D+bgfile).convert('RGB').crop((0,0,360,42)),(0,0))
    if peak is not None:
        from design import VIZ
        for (name,x,h,ch),lv in zip(VIZ['bars'],peak):
            y=VIZ['bottom']-h; im.paste(Image.open(D+name+'d.bmp'),(x,y)); f=int(round(h*lv))
            if f: im.paste(Image.open(D+name+'l.bmp').crop((0,h-f,5,h)),(x,y+h-f))
    else:
        text(im,(30,8,48,26),'-3',f8,T['status'],'r'); text(im,(80,0,30,16),'.5',f5,T['status'],'l'); text(im,(80,16,30,16),'dB',f5,T['status'],'l')
    if peak is not None: text(im,(11,8,120,27),'21:36',f8,T['status'],'l')
    else: text(im,(120,8,120,27),'21:36',f8,T['status'],'c')
    if charging:
        text(im,(240,8,78,26),batt,f8,T['status'],'r'); mono(im,D+'bolt.bmp',322,12,0,1,ACCENT_HEX)
    else: text(im,(254,8,78,26),batt,f8,T['status'],'r')
    lvl=int(batt[:-1]); im.paste(Image.open(D+'batt_empty.bmp'),(340,16)); fl=Image.open(D+'batt_level.bmp'); h=int(round(14*lvl/100))
    if h: im.paste(fl.crop((0,14-h,6,14)),(340,16+14-h))
status_bar(u,'78%',True,peak=(),bgfile='sbs_bg.bmp')
text(u,(34,354,150,53),'78%',f56,'f6f1fb','l')
text(u,(170,362,156,20),'Charging',f20,ACCENT_HEX,'r')
text(u,(170,386,156,20),'4.12 V',f20,'9d8fb0','r')
tr=Image.open(D+'batt_track.bmp'); fl=Image.open(D+'batt_fill.bmp'); u.paste(tr,(34,424)); w=int(292*0.78); u.paste(fl.crop((0,0,w,14)),(34,424))
text(u,(176,493,150,20),'Connected',f20,'ddd3e8','r'); text(u,(176,525,150,20),'7h 42m',f20,'ddd3e8','r')
u.save('/home/user/scratch/v4_usb.png')
a2=render(art,s); status_bar(a2,'78%',False,peak=(0.8,0.6,0.75,0.55,0.7))
c=Image.new('RGB',(360*3+40,640),(255,255,255)); c.paste(a2,(0,0)); c.paste(u,(380,0)); status_bar(sb,'78%',True,peak=(),bgfile='sbs_bg.bmp'); c.paste(sb,(760,0)); c.save('/home/user/scratch/v4_all.png')
