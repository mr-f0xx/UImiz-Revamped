import os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from design import L, ACCENT_HEX, build_all, TEXT_HEX as T, P

OUT = '/home/user/UImiz-Revamped-AP80ProMax/'
R = OUT + '.rockbox/'
FONTS = '/home/user/scratch/fonts/'
A = ACCENT_HEX

if os.path.exists(R):
    shutil.rmtree(R)
for d in ['wps/UImiz Revamped', 'icons', 'fonts', 'themes']:
    os.makedirs(R + d, exist_ok=True)

# ---- bitmaps
build_all(R + 'wps/UImiz Revamped/')
old = '/home/user/JGUlmiz-AP80ProMax-v1/.rockbox/'
shutil.copy(old + 'wps/JGUlmiz/JGUlmiz_24.bmp', R + 'wps/UImiz Revamped/title_icons.bmp')
# Rockbox only loads icon sets from /.rockbox/icons (apps/gui/icon.c load_icons)
shutil.copy(old + 'icons/ulmiz_icons.bmp', R + 'icons/UImiz Revamped icons.bmp')
shutil.copy(old + 'icons/ulmiz_viewer.bmp', R + 'icons/UImiz Revamped viewers.bmp')
for f in ['27-Ubuntu-Regular', '34-Ubuntu-Medium', '34-Ubuntu-Bold', '38-Ubuntu-Medium',
          '16-Ubuntu-Medium', '180-Ubuntu-Bold', '56-Ubuntu-Medium', '20-Ubuntu-Medium']:
    shutil.copy(FONTS + f + '.fnt', R + 'fonts/')


def box_vp(b):
    x0, y0, x1, y1 = b
    return f'{x0},{y0},{x1 - x0},{y1 - y0}'


HDR = lambda kind: f"""# Rockbox Theme Name: UImiz Revamped (HIDIZS AP80 Pro Max)
# Platform: HIDIZS AP80 Pro Max (360x640)
# Based on JGUlmiz for the HiBy R1 by jgoedde, and Ulmiz by Simon Rothen (rothen@gmx.net)
# Licencing: CC-BY-SA 3.0
# iconset taken from advaitapod theme vector files
#
# Version: 2.0-ap80pm
# Date: 2026-10-01
#
# {kind}
#
"""
VOL_INT = "%?if(%pv,<=,-1000)<%ss(0,4,%pv)|%?if(%pv,>,-100)<%?if(%pv,>=,0)<%ss(0,1,%pv)|%ss(0,2,%pv)>|%ss(0,3,%pv)>>"
VOL_DEC = "%?if(%pv,<=,-1000)<%ss(4,2,%pv)|%?if(%pv,>,-100)<%?if(%pv,>=,0)<%ss(1,2,%pv)|%ss(2,2,%pv)>|%ss(3,2,%pv)>>"


def status(wps):
    # status bar 0..42: everything vertically centred on y=21, 12 px side margins.
    # Now Playing: clock left, tiny 5-bar visualizer (peak-meter bars) centred, battery right.
    # Menus: same layout without the visualizer (the menu status bar only redraws ~1x/s when idle).
    # Battery outline is part of both backdrops.
    c = T['status']
    vol = ""
    if wps:  # visualizer only on Now Playing (menus can't animate it smoothly)
        from design import VIZ
        bars = []
        for name, x, h, ch in VIZ['bars']:
            y = VIZ['bottom'] - h
            bars.append(f"""%xl({name}l,{name}l.bmp,0,0)
%xl({name}d,{name}d.bmp,0,0)
%V({x},{y},{VIZ['w']},{h},-)
%p{ch}(0,0,{VIZ['w']},{h},vertical,image,{name}l,backdrop,{name}d)""")
        vol = "# Visualizer  (centred; left / right peak levels)\n" + "\n".join(bars) + "\n"
    clock = f"""# Clock  (left, 12 px from the edge like the battery on the right)
%V(11,8,120,27,8)%Vf({c})
%al%?cf<%ck:%cM|%cl:%cM %cp>
"""
    if not wps:  # menus: tap the visualizer (centre third of the status bar) for the quick screen
        clock += """%V(120,0,120,42,-)
%T(0,0,-,-,quickscreen)
"""
    return vol + "#\n" + clock + f"""#
# Battery  (percentage moves left and a purple bolt appears while the charger is connected)
%?bp<%Vd(bchg)|%Vd(bnorm)>
%Vl(bnorm,254,8,78,26,8)%Vf({c})
%ar%bl%%
%Vl(bchg,240,8,78,26,8)%Vf({c})
%ar%bl%%
%xl(z,bolt.bmp,0,0)
%Vl(bchg,322,12,10,18,-)%Vf({A})
%xd(z)
# battery level: pastel purple fill inside the white outline (outline is in the backdrop)
%xl(bf,batt_level.bmp,0,0)
%xl(be,batt_empty.bmp,0,0)
%V(340,16,6,14,-)
%bl(0,0,6,14,vertical,image,bf,backdrop,be)
"""


ax, ay, aw, ah = L['art']
al, yr, ar_, ti = L['album'], L['year'], L['artist'], L['title']
tx0, ty0, tx1, ty1 = L['track']


def txt_vp(pill, font_off, h, pad=6):
    x0, y0, x1, y1 = pill
    cy = (y0 + y1) / 2
    return f'{x0 + pad},{int(round(cy - font_off))},{x1 - x0 - 2 * pad},{h}'


wps = HDR("WPS File") + f"""# Additional Fonts
%Fl(7,34-Ubuntu-Bold.fnt)
%Fl(4,38-Ubuntu-Medium.fnt)
%Fl(8,27-Ubuntu-Regular.fnt)
%Fl(5,16-Ubuntu-Medium.fnt)
%Fl(6,180-Ubuntu-Bold.fnt)
#
# Disable Status Bar
%wd
#
%V(0,0,-,-,-)%VB
%x(backdrop,wps_bg.bmp,0,0)
#
%V(0,0,-,-,-)
# albumart, or big volume while the volume is being changed
%?mv(1.5)<%Vd(volumen)|%Vd(albumart)>
#
### Touch Areas
# status bar touch zones: clock = menu, visualizer (centre) = quick screen, battery = context menu
%T(0,0,120,42,menu)
%T(120,0,120,42,quickscreen)
%T(240,0,-,42,contextmenu)
%T(0,{ay},-,150,browse,long_press)
%T(playlist,0,{ay + 150},-,150,playlist,long_press)
%T(infoscreen,0,{ay},-,{aw},none)
#
### VIEWPORTS
{status(True)}#
# Albumart
%Vl(albumart,{ax},{ay},{aw},{ah},-)
%Cl(0,0,{aw},{ah},c,c)
%?C<%Cd>
#
# Volume Big (shown over the album art area while changing volume)
%Vl(volumen,0,{ay + ah // 2 - 85},-,170,6)%Vf({T['status']})
%ac{VOL_INT}
#
# Album
%V({txt_vp(al, 13, 26, 4)},8)%Vf({T['album']})%Vb(31283c)
%s%ac%?id<%id>
#
# Year
%V({txt_vp(yr, 13, 26, 2)},8)%Vf({T['year']})%Vb(c0b2d0)
%ac%?iy<%ss(0,4,%iy)>
#
# Artist
%V({txt_vp(ar_, 17.5, 33, 8)},7)%Vf({T['artist']})%Vb(271f32)
%s%ac%ia
#
# Title
%V({txt_vp(ti, 19, 36, 8)},4)%Vf({T['title']})%Vb(f0ecf6)
%s%ac%?mp<|%it|%t(0.5)%it;%t(0.5)|%pc %>%>|%<%< %pc|%it>
#
# Progressbar (track is drawn in the backdrop, rockbox draws the purple border + fill)
%V(0,{ty0 - 9},-,{ty1 - ty0 + 17},-)%Vb(16111c)%Vf({A})
%T(seek,0,0,-,-,progressbar)
%pb({tx0},9,{tx1 - tx0},{ty1 - ty0},notouch)
#
# Time elapsed
%V({tx0},{ty1 + 8},90,26,8)%Vf({T['times']})
%al%pc
#
# Time total
%V({tx1 - 90},{ty1 + 8},90,26,8)%Vf({T['times']})
%ar%pt
#
# Playlist position
%V(100,{ty1 + 8},160,26,8)%Vf({T['times']})
%ac%s%pp %Sx(of) %pe
#
# Shuffle  (frame a = off, b = on)
%xl(s,shuffle.bmp,0,0,2)
%V({box_vp(L['shuffle'])},-)
%T(shuffle,0,0,-,-,shuffle)
%?ps<%xd(sb)|%xd(sa)>
#
# Previous, Rewind
%V({box_vp(L['prev'])},-)
%T(0,0,-,-,rwd,repeat_press)
%T(rr,0,0,-,-,wps_prev)
#
# Play, Pause, Stop  (frame a = stop, b = play, c = pause)
%xl(p,play.bmp,0,0,3)
%V({box_vp(L['play'])},-)
#Stop, Play, Pause, Fast Forward, Rewind
%?mp<%xd(pa)|%xd(pc)|%xd(pb)|%xd(pc)|%xd(pc)>
%T(0,0,-,-,stop,long_press)
%T(play,0,0,-,-,play)
#
# Next, Forward
%V({box_vp(L['next'])},-)
%T(0,0,-,-,ffwd,repeat_press)
%T(ff,0,0,-,-,wps_next)
#
# Repeat mode  (a = off, b = all, c = one, d = shuffle, e = A-B)
%xl(r,repeat.bmp,0,0,5)
%V({box_vp(L['repeat'])},-)
%T(repeat,0,0,-,-,repmode)
%T(0,0,-,-,setting_set,repeat,off,long_press)
%?mm<%xd(ra)|%xd(rb)|%xd(rc)|%xd(rd)|%xd(re)>
"""

icons = '|'.join('%xd(t' + c + ')' for c in 'abcdefghijklmnopqrstuvwxyzABCDEF')
sbs = HDR("SBS File") + f"""# Additional Fonts
%Fl(3,34-Ubuntu-Medium.fnt)
%Fl(4,38-Ubuntu-Medium.fnt)
%Fl(8,27-Ubuntu-Regular.fnt)
%Fl(5,16-Ubuntu-Medium.fnt)
%Fl(9,56-Ubuntu-Medium.fnt)
%Fl(10,20-Ubuntu-Medium.fnt)
#
%X(sbs_bg.bmp)
#
# USB screen (activity 21): own layout, hide the menu title, park the built-in USB logo in a 1px UI viewport
%?if(%cs,=,21)<%VI(usbvi)|%VI(menu)>
%?if(%cs,=,21)<%Vd(usb)|%Vd(title)>
#
# Cancel
%V(38,574,60,45,-)
%T(cancel,0,0,-,-,cancel)
%T(cancel,0,0,-,-,menu,long_press)
#
# Resume (Go to WPS)
%V(263,574,60,45,-)
%T(0,0,-,-,resumeplayback)
#
### VIEWPORTS
## Vi AREA (MENU)  7 lines x 66px (33px font + 33 padding)
%Vi(menu,15,98,334,465,1)
%Vi(usbvi,359,639,1,1,-)
#
### USB SCREEN
%xl(U,usb_screen.bmp,0,0)
%xl(f,batt_fill.bmp,0,0)
%xl(g,batt_track.bmp,0,0)
%Vl(usb,0,42,-,-,-)
%xd(U)
# battery percentage (big)
%Vl(usb,34,354,150,53,9)%Vf(f6f1fb)
%al%bl%%
# charging state
%Vl(usb,170,362,156,20,10)%Vf({A})
%ar%?bc<Charging|%?bp<Fully charged|On battery>>
# voltage
%Vl(usb,170,386,156,20,10)%Vf(9d8fb0)
%ar%bv V
# battery bar
%Vl(usb,34,424,292,14,-)%Vf({A})
%bl(0,0,292,14,image,f,backdrop,g)
# charger / runtime rows
%Vl(usb,176,493,150,20,10)%Vf(ddd3e8)
%ar%?bp<Connected|Not connected>
%Vl(usb,176,525,150,20,10)%Vf(ddd3e8)
%ar%bt
#
{status(False)}#
# Title
%xl(t,title_icons.bmp,0,0,32)
%Vl(title,5,61,30,38,-)%Vf({A})
%?Li<|{icons}>
%Vl(title,41,53,-22,38,4)%Vf({A})
%s%Lt
%T(0,0,-,-,cancel)
"""

cfg = f"""# Rockbox Theme Name: UImiz Revamped (HIDIZS AP80 Pro Max)
# Platform: HIDIZS AP80 Pro Max (360x640)
# Based on JGUlmiz for the HiBy R1 by jgoedde, and Ulmiz by Simon Rothen (rothen@gmx.net)
# Licencing: CC-BY-SA 3.0
#
# Version: 2.0-ap80pm
# Date: 2026-10-01
#

wps: /.rockbox/wps/UImiz Revamped.wps
sbs: /.rockbox/wps/UImiz Revamped.sbs
foreground color: ddd3e8
background color: 211a29
font: /.rockbox/fonts/34-Ubuntu-Medium.fnt
iconset: /.rockbox/icons/UImiz Revamped icons.bmp
viewers iconset: /.rockbox/icons/UImiz Revamped viewers.bmp
backdrop: -
show icons: on
filetype colours: -
scrollbar: right
scrollbar width: 30
selector type: bar (color)
statusbar: top
line selector text color: 1e1626
line selector end color: {A}
line selector start color: {A}
ui viewport: -
list padding: 33
"""
crlf = lambda s: s.replace('\n', '\r\n')
open(R + 'wps/UImiz Revamped.wps', 'w', newline='').write(crlf(wps))
open(R + 'wps/UImiz Revamped.sbs', 'w', newline='').write(crlf(sbs))
open(R + 'themes/UImiz Revamped.cfg', 'w').write(cfg)
print('built')
