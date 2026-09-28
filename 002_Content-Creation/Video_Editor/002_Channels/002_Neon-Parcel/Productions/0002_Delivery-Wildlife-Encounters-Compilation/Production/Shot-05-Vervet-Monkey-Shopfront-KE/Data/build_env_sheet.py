from PIL import Image, ImageDraw, ImageFont, ImageFilter
D='Data/'
FB='/System/Library/Fonts/Supplemental/Arial Bold.ttf'; FR='/System/Library/Fonts/Supplemental/Arial.ttf'
f=lambda s,b=True: ImageFont.truetype(FB if b else FR,s)
BG=(15,19,25); CARD=(24,30,39); LINE=(58,68,82); TXT=(236,240,245); MUT=(150,160,174)
TEAL=(46,196,176); ORG=(244,148,48)
GUT=360; IW,IH=1280,720; CW=GUT*2+IW; TITLE=112; LEG=120; CH=TITLE+IH+LEG
M=60; GAP=50; HEAD=170; BAND=340
W=M*2+CW*2+GAP; H=HEAD+GAP+CH*2+GAP+GAP+BAND+M
sh=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(sh)
# header
d.rectangle([0,0,W,HEAD],fill=(10,13,18)); d.rectangle([0,HEAD-6,W,HEAD],fill=TEAL)
d.text((M,26),"ENVIRONMENT SHEET",font=f(74),fill=TXT)
d.text((M+d.textlength("ENVIRONMENT SHEET",font=f(74))+50,26),"SHOT 05  |  VERVET MONKEY SHOPFRONT  |  CENTRAL KENYA",font=f(74),fill=TEAL)
d.text((M,116),"FIXED STATIC SHOPFRONT CCTV   -   CLEAR HOT MIDDAY SUN, DRY SEASON   -   PANEL 1 IS THE CAMERA'S VIEW (16:9)",font=f(32,False),fill=MUT)
def wrap(t,font,maxw):
    out=[]; 
    for para in t.split('\n'):
        cur=''
        for w in para.split():
            tr=(cur+' '+w).strip()
            if d.textlength(tr,font=font)<=maxw: cur=tr
            else: out.append(cur); cur=w
        out.append(cur)
    return out
def chip(x_edge,side,cy,label,px,py,accent):
    fo=f(27); lines=wrap(label,fo,GUT-70); wmax=max(d.textlength(l,font=fo) for l in lines); bw=int(wmax+40); bh=36*len(lines)+22
    x0=x_edge-bw if side=='L' else x_edge; ty=cy-bh//2
    ex=x0+bw if side=='L' else x0
    d.line([(ex,cy),(px,py)],fill=accent,width=4); d.ellipse([px-13,py-13,px+13,py+13],fill=accent,outline=BG,width=4)
    d.rounded_rectangle([x0,ty,x0+bw,ty+bh],radius=10,fill=(10,13,18),outline=accent,width=3)
    for i,l in enumerate(lines): d.text((x0+bw//2,ty+11+36*i+18),l,font=fo,fill=TXT,anchor='mm')
def cell(col,row,num,title,sub,img,legend,marks=()):
    x0=M+col*(CW+GAP); y0=HEAD+GAP+row*(CH+GAP)
    d.rounded_rectangle([x0,y0,x0+CW,y0+CH],radius=16,fill=CARD,outline=LINE,width=3)
    d.ellipse([x0+26,y0+20,x0+96,y0+90],fill=ORG); d.text((x0+61,y0+55),str(num),font=f(44),fill=(15,19,25),anchor='mm')
    d.text((x0+120,y0+10),title,font=f(46),fill=TXT); d.text((x0+120,y0+66),sub,font=f(27,False),fill=MUT)
    d.line([(x0+26,y0+TITLE-4),(x0+CW-26,y0+TITLE-4)],fill=TEAL,width=3)
    im=Image.open(img).convert('RGB'); s=min(IW/im.width,IH/im.height); im=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
    ix=x0+GUT+(IW-im.width)//2; iy=y0+TITLE+(IH-im.height)//2
    d.rectangle([ix-5,iy-5,ix+im.width+5,iy+im.height+5],outline=(200,208,220),width=4); sh.paste(im,(ix,iy))
    for side in 'LR':
        ms=sorted([m for m in marks if m[3]==side],key=lambda m:m[1])
        n=len(ms)
        for k,(fx,fy,label,_,acc) in enumerate(ms):
            cy=y0+TITLE+int((k+0.5)*IH/n); px=ix+int(fx*im.width); py=iy+int(fy*im.height)
            chip(x0+GUT-22 if side=='L' else x0+GUT+IW+22,side,cy,label,px,py,acc)
    ly=y0+TITLE+IH
    for i,l in enumerate(legend): d.text((x0+30,ly+18+i*40),l,font=f(28,i==0),fill=TXT if i==0 else MUT)
cell(0,0,1,"CAMERA POV","The static CCTV view - exactly what the video frame shows",D+'Shopfront_Panel_3_POV.png',
 ["CAMERA'S VIEW  |  16:9, fixed, high under the awning edge, looking down at the counter and apron","Every landmark here is in frame. The counter TOP is barely visible from this angle - see panels 3 and 4."],
 marks=[(0.245,0.135,"CCTV BOX",'L',TEAL),(0.22,0.30,"AWNING POST (MONKEY PERCH)",'L',ORG),(0.35,0.85,"DIRT APRON",'L',TEAL),
        (0.55,0.20,"CORRUGATED-IRON AWNING",'R',TEAL),(0.52,0.43,"CLIPBOARD SET-DOWN (COUNTER TOP)",'R',ORG),(0.52,0.58,"WOODEN COUNTER (FRONT PANEL)",'R',TEAL),(0.75,0.78,"BICYCLE STOP POINT",'R',ORG)])
cell(1,0,2,"TOP-DOWN VIEW","Bird's-eye site plan - the single source of truth for positions",D+'Shopfront_Panel_1_TopDown_Unlabeled.png',
 ["PLAN VIEW  |  the camera sits under the awning edge and looks toward the bottom of this plan (the apron)","Orange = action points for the gag (perch, clipboard, bicycle).  Teal = fixed set structure."],
 marks=[(0.50,0.20,"SHOP INTERIOR",'L',TEAL),(0.30,0.355,"AWNING POST (MONKEY PERCH)",'L',ORG),(0.40,0.555,"WOODEN COUNTER",'L',TEAL),
        (0.50,0.42,"CORRUGATED-IRON AWNING",'R',TEAL),(0.489,0.563,"CLIPBOARD SET-DOWN POINT",'R',ORG),(0.66,0.77,"BICYCLE STOP POINT",'R',ORG)])
cell(0,1,3,"REVERSE VIEW","Spatial reference ONLY - NOT camera output. Behind the counter, looking out",D+'Shopfront_Panel_4_Reverse.png',
 ["REVERSE ANGLE  |  standing inside the shop behind the counter, looking out at the apron and street wall","Shows the flat counter top and the awning post from the opposite side. The real camera never sees this."],
 marks=[(0.125,0.17,"CCTV BOX",'L',TEAL),(0.145,0.42,"AWNING POST (MONKEY PERCH ON TOP)",'L',ORG),
        (0.62,0.20,"AWNING (UNDERSIDE)",'R',TEAL),(0.57,0.30,"STREET GATE + BOUNDARY WALL",'R',TEAL),(0.5,0.52,"DIRT APRON",'R',TEAL),(0.5,0.76,"COUNTER TOP (CLIPBOARD SET-DOWN)",'R',ORG)])
cell(1,1,4,"LANDMARK DETAIL","The recurring set objects the video prompts refer to by name",D+'Shopfront_Panel_5_LandmarkDetail.png',
 ["A COUNTER + clipboard point  |  B POST + monkey perch  |  C BICYCLE ON KICKSTAND  |  D CCTV BOX","These objects must look identical in every frame of the video."],
 marks=[(0.25,0.25,"A  WOODEN COUNTER + CLIPBOARD POINT",'L',ORG),(0.25,0.75,"C  PARCEL BICYCLE ON KICKSTAND (NEVER FLOATS)",'L',TEAL),
        (0.75,0.25,"B  AWNING POST WITH MONKEY PERCH ON TOP",'R',ORG),(0.75,0.75,"D  CCTV CAMERA BOX UNDER AWNING",'R',TEAL)])
# bottom band: materials / palette / details
by=HEAD+GAP+CH*2+GAP*2
d.rounded_rectangle([M,by,W-M,by+BAND],radius=16,fill=CARD,outline=LINE,width=3)
P3=Image.open(D+'Shopfront_Panel_3_POV.png').convert('RGB'); P4=Image.open(D+'Shopfront_Panel_4_Reverse.png').convert('RGB'); P5=Image.open(D+'Shopfront_Panel_5_LandmarkDetail.png').convert('RGB')
def tile(im,box,size):
    c=im.crop(box); r=size[0]/size[1]
    if c.width/c.height>r:
        nw=int(c.height*r); x=(c.width-nw)//2; c=c.crop((x,0,x+nw,c.height))
    else:
        nh=int(c.width/r); y=(c.height-nh)//2; c=c.crop((0,y,c.width,y+nh))
    return c.resize(size,Image.LANCZOS)
mats=[("CORRUGATED IRON",tile(P5,(1800,790,2250,1000),(150,150))),("WEATHERED WOOD",tile(P5,(450,400,900,620),(150,150))),
      ("DRY DIRT",tile(P3,(820,1160,1230,1370),(150,150))),("BLOCK WALL",tile(P4,(720,290,1020,410),(150,150))),
      ("RUSTED STEEL POST",tile(P5,(1897,320,2097,520),(150,150))),("CLIPBOARD BEIGE",tile(P5,(240,190,470,290),(150,150)))]
x=M+30; d.text((x,by+18),"MATERIALS & COLORS",font=f(34),fill=TEAL)
for i,(n,t) in enumerate(mats):
    tx=x+i*175; d.rectangle([tx-3,by+72,tx+153,by+228],outline=LINE,width=3); sh.paste(t,(tx,by+75)); [d.text((tx+75,by+238+22*i),l,font=f(18),fill=TXT,anchor='mm') for i,l in enumerate(wrap(n,f(18),168))]
px0=x+6*175+50; d.text((px0,by+18),"COLOR PALETTE",font=f(34),fill=TEAL)
q=P3.resize((300,170)).quantize(colors=8,method=Image.Quantize.MEDIANCUT).convert('RGB'); cols=sorted(q.getcolors(),reverse=True)
for i,(cnt,c) in enumerate(cols[:8]):
    cx=px0+i*118; d.rounded_rectangle([cx,by+75,cx+104,by+215],radius=10,fill=c,outline=LINE,width=3); d.text((cx+52,by+245),'#%02X%02X%02X'%c,font=f(20,False),fill=TXT,anchor='mm')
dx=px0+8*118+40; d.text((dx,by+18),"DETAILS",font=f(34),fill=TEAL)
dets=[("AWNING ROOF",tile(P5,(1640,770,2325,1070),(250,150))),("PLANK COUNTER",tile(P5,(350,330,1250,700),(250,150))),("POST + PERCH",tile(P5,(1900,25,2090,410),(150,150))),("CCTV BOX",tile(P5,(1710,1067,2030,1313),(150,150)))]
xx=dx
for n,t in dets:
    d.rectangle([xx-3,by+72,xx+t.width+3,by+72+t.height+6],outline=LINE,width=3); sh.paste(t,(xx,by+75)); d.text((xx+t.width//2,by+245),n,font=f(19),fill=TXT,anchor='mm'); xx+=t.width+28
d.text((M+30,by+BAND-60),"KEY:  ORANGE = gag action points (monkey perch, clipboard set-down, bicycle stop)     TEAL = fixed set structure     Labels sit in the margins and never cover the images.",font=f(26,False),fill=MUT)
sh.save('Character_Sheets/Environment_Sheet_v2.png'); print(sh.size)
