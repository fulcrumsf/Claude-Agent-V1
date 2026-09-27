#!/usr/bin/env python3
"""Render an environment sheet (dark presentation-board style) from a JSON spec.
Usage: python3 build_environment_sheet.py <spec.json> --base <production_folder> --out <sheet.png>
All image paths in the spec are relative to --base. See Examples/ for a full spec."""
import json, argparse, os
from PIL import Image, ImageDraw, ImageFont

def load_font(bold, size):
    cands = (["/System/Library/Fonts/Supplemental/Arial Bold.ttf","/Library/Fonts/Arial Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","C:/Windows/Fonts/arialbd.ttf"]
             if bold else ["/System/Library/Fonts/Supplemental/Arial.ttf","/Library/Fonts/Arial.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","C:/Windows/Fonts/arial.ttf"])
    for c in cands:
        if os.path.exists(c): return ImageFont.truetype(c, size)
    return ImageFont.load_default()

BG=(15,19,25); CARD=(24,30,39); LINE=(58,68,82); TXT=(236,240,245); MUT=(150,160,174)
ACC={'teal':(46,196,176),'orange':(244,148,48)}

def render(spec, base, out):
    F=lambda s,b=True: load_font(b,s)
    GUT=360; IW,IH=1280,720; TITLE=112; LEG=120; CH=TITLE+IH+LEG; CW=GUT*2+IW
    M=60; GAP=50; HEAD=170
    cols=spec.get('cols',2); panels=spec['panels']; rows=(len(panels)+cols-1)//cols
    has_band=any(k in spec for k in ('materials','details','palette'))
    BAND=340 if has_band else 0
    W=M*2+CW*cols+GAP*(cols-1); H=HEAD+GAP+CH*rows+GAP*(rows-1)+((GAP+BAND) if has_band else 0)+M
    sh=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(sh)
    P=lambda p: os.path.join(base,p)
    d.rectangle([0,0,W,HEAD],fill=(10,13,18)); d.rectangle([0,HEAD-6,W,HEAD],fill=ACC['teal'])
    t1=spec.get('title','ENVIRONMENT SHEET'); d.text((M,26),t1,font=F(74),fill=TXT)
    d.text((M+d.textlength(t1,font=F(74))+50,26),spec.get('headline',''),font=F(74),fill=ACC['teal'])
    d.text((M,116),spec.get('subtitle',''),font=F(32,False),fill=MUT)
    def wrap(t,font,maxw):
        out_=[]
        for para in t.split('\n'):
            cur=''
            for w in para.split():
                tr=(cur+' '+w).strip()
                if d.textlength(tr,font=font)<=maxw: cur=tr
                else: out_.append(cur); cur=w
            out_.append(cur)
        return out_
    def chip(x_edge,side,cy,label,px,py,accent):
        fo=F(27); lines=wrap(label,fo,GUT-70); bw=int(max(d.textlength(l,font=fo) for l in lines)+40); bh=36*len(lines)+22
        x0=x_edge-bw if side=='L' else x_edge; ty=cy-bh//2; ex=x0+bw if side=='L' else x0
        d.line([(ex,cy),(px,py)],fill=accent,width=4); d.ellipse([px-13,py-13,px+13,py+13],fill=accent,outline=BG,width=4)
        d.rounded_rectangle([x0,ty,x0+bw,ty+bh],radius=10,fill=(10,13,18),outline=accent,width=3)
        for i,l in enumerate(lines): d.text((x0+bw//2,ty+11+36*i+18),l,font=fo,fill=TXT,anchor='mm')
    for idx,pn in enumerate(panels):
        col,row=idx%cols,idx//cols; x0=M+col*(CW+GAP); y0=HEAD+GAP+row*(CH+GAP)
        d.rounded_rectangle([x0,y0,x0+CW,y0+CH],radius=16,fill=CARD,outline=LINE,width=3)
        d.ellipse([x0+26,y0+20,x0+96,y0+90],fill=ACC['orange']); d.text((x0+61,y0+55),str(pn.get('num',idx+1)),font=F(44),fill=(15,19,25),anchor='mm')
        d.text((x0+120,y0+10),pn['title'],font=F(46),fill=TXT); d.text((x0+120,y0+66),pn.get('subtitle',''),font=F(27,False),fill=MUT)
        d.line([(x0+26,y0+TITLE-4),(x0+CW-26,y0+TITLE-4)],fill=ACC['teal'],width=3)
        im=Image.open(P(pn['image'])).convert('RGB'); s=min(IW/im.width,IH/im.height); im=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
        ix=x0+GUT+(IW-im.width)//2; iy=y0+TITLE+(IH-im.height)//2
        d.rectangle([ix-5,iy-5,ix+im.width+5,iy+im.height+5],outline=(200,208,220),width=4); sh.paste(im,(ix,iy))
        marks=pn.get('marks',[])
        for side in 'LR':
            ms=sorted([m for m in marks if m['side']==side],key=lambda m:m['fy']); n=len(ms)
            for k,m in enumerate(ms):
                cy=y0+TITLE+int((k+0.5)*IH/n); px=ix+int(m['fx']*im.width); py=iy+int(m['fy']*im.height)
                chip(x0+GUT-22 if side=='L' else x0+GUT+IW+22,side,cy,m['label'],px,py,ACC[m.get('accent','teal')])
        ly=y0+TITLE+IH
        for i,l in enumerate(pn.get('legend',[])): d.text((x0+30,ly+18+i*40),l,font=F(28,i==0),fill=TXT if i==0 else MUT)
        for b in pn.get('badges',[]):   # letter badges inside a multi-object panel, fractions of the image
            bx=ix+int(b['fx']*im.width); by_=iy+int(b['fy']*im.height)
            d.ellipse([bx,by_,bx+64,by_+64],fill=ACC['orange'],outline=BG,width=3); d.text((bx+32,by_+32),b['text'],font=F(38),fill=(15,19,25),anchor='mm')
    if has_band:
        by=HEAD+GAP+CH*rows+GAP*(rows-1)+GAP
        d.rounded_rectangle([M,by,W-M,by+BAND],radius=16,fill=CARD,outline=LINE,width=3)
        def tile(im,box,size):
            c=im.crop(tuple(box)); r=size[0]/size[1]
            if c.width/c.height>r: nw=int(c.height*r); x=(c.width-nw)//2; c=c.crop((x,0,x+nw,c.height))
            else: nh=int(c.width/r); y=(c.height-nh)//2; c=c.crop((0,y,c.width,y+nh))
            return c.resize(size,Image.LANCZOS)
        cache={}
        def img(p):
            if p not in cache: cache[p]=Image.open(P(p)).convert('RGB')
            return cache[p]
        x=M+30; mats=spec.get('materials',[])
        if mats:
            d.text((x,by+18),"MATERIALS & COLORS",font=F(34),fill=ACC['teal'])
            for i,m in enumerate(mats):
                t=tile(img(m['image']),m['crop'],(150,150)); tx=x+i*175
                d.rectangle([tx-3,by+72,tx+153,by+228],outline=LINE,width=3); sh.paste(t,(tx,by+75))
                for j,l in enumerate(wrap(m['name'],F(18),168)): d.text((tx+75,by+238+22*j),l,font=F(18),fill=TXT,anchor='mm')
        px0=x+max(len(mats),1)*175+50
        pal=spec.get('palette')
        if pal:
            d.text((px0,by+18),"COLOR PALETTE",font=F(34),fill=ACC['teal'])
            src=img(pal['image']); q=src.resize((300,170)).quantize(colors=pal.get('count',8),method=Image.Quantize.MEDIANCUT).convert('RGB')
            cols_=sorted(q.getcolors(),reverse=True)
            for i,(cnt,c) in enumerate(cols_[:pal.get('count',8)]):
                cx=px0+i*118; d.rounded_rectangle([cx,by+75,cx+104,by+215],radius=10,fill=c,outline=LINE,width=3); d.text((cx+52,by+245),'#%02X%02X%02X'%c,font=F(20,False),fill=TXT,anchor='mm')
            px0=px0+pal.get('count',8)*118+40
        dets=spec.get('details',[])
        if dets:
            d.text((px0,by+18),"DETAILS",font=F(34),fill=ACC['teal']); xx=px0
            for dt in dets:
                sz=tuple(dt.get('size',[150,150])); t=tile(img(dt['image']),dt['crop'],sz)
                d.rectangle([xx-3,by+72,xx+sz[0]+3,by+72+sz[1]+6],outline=LINE,width=3); sh.paste(t,(xx,by+75))
                d.text((xx+sz[0]//2,by+245),dt['name'],font=F(19),fill=TXT,anchor='mm'); xx+=sz[0]+28
        if spec.get('key'): d.text((M+30,by+BAND-60),spec['key'],font=F(26,False),fill=MUT)
    os.makedirs(os.path.dirname(os.path.abspath(out)),exist_ok=True); sh.save(out); return sh.size

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('--base',required=True); ap.add_argument('--out',required=True)
    a=ap.parse_args(); print(render(json.load(open(a.spec)),a.base,a.out))
