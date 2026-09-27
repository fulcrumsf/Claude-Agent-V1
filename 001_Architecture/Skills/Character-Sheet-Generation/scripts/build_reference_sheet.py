#!/usr/bin/env python3
"""Render a CHARACTER / CREATURE / PROP reference sheet in the shared dark presentation-board style
(same look as Environment-Sheet-Generation/scripts/build_environment_sheet.py).
Usage: python3 build_reference_sheet.py <spec.json> --base <production_folder> --out <sheet.png>
Spec: {title, headline, subtitle, width?, rows:[{h?, items:[ panel | block ]}]}
 panel: {type:'panel', num, title, image, legend?}   (width follows the image's aspect; all panels in a row share a height)
 block: {type:'notes'|'scale'|'swatches'|'palette', title, w? (px) or flex:1 ...}"""
import json, argparse, os
from PIL import Image, ImageDraw, ImageFont
def font(bold,size):
    c=(["/System/Library/Fonts/Supplemental/Arial Bold.ttf","/Library/Fonts/Arial Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","C:/Windows/Fonts/arialbd.ttf"] if bold else
       ["/System/Library/Fonts/Supplemental/Arial.ttf","/Library/Fonts/Arial.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","C:/Windows/Fonts/arial.ttf"])
    for p in c:
        if os.path.exists(p): return ImageFont.truetype(p,size)
    return ImageFont.load_default()
BG=(15,19,25); CARD=(24,30,39); LINE=(58,68,82); TXT=(236,240,245); MUT=(150,160,174); TEAL=(46,196,176); ORG=(244,148,48)
def render(spec,base,out):
    F=lambda s,b=True: font(b,s); W=spec.get('width',4200); M=60; G=30; HEAD=170; TS=84; LS=64
    P=lambda p: os.path.join(base,p); cache={}
    def img(p):
        if p not in cache: cache[p]=Image.open(P(p)).convert('RGB')
        return cache[p]
    tmp=ImageDraw.Draw(Image.new('RGB',(10,10)))
    def wrap(t,fo,mw):
        o=[]
        for para in t.split('\n'):
            cur=''
            for w in para.split():
                tr=(cur+' '+w).strip()
                if tmp.textlength(tr,font=fo)<=mw: cur=tr
                else: o.append(cur); cur=w
            o.append(cur)
        return o
    Wi=W-2*M; rows=[]; Htot=HEAD+G
    for r in spec['rows']:
        items=r['items']; pan=[i for i in items if i['type']=='panel']; blk=[i for i in items if i['type']!='panel']
        asp=[ (lambda im: im.width/im.height)(img(p['image'])) for p in pan]
        fixed=sum(b.get('w',0) for b in blk); flexn=sum(b.get('flex',0) for b in blk)
        if 'h' in r: h=r['h']
        else: h=int((Wi-G*(len(items)-1)-fixed)/max(sum(asp),0.01))
        pw=[int(a*h) for a in asp]
        left=Wi-G*(len(items)-1)-sum(pw)-fixed
        for b in blk: b['_w']=b.get('w') or int(left*b.get('flex',1)/max(flexn,1))
        ch=TS+h+LS
        rows.append((r,h,pw,ch)); Htot+=ch+G
    H=Htot+M-G
    sh=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(sh)
    d.rectangle([0,0,W,HEAD],fill=(10,13,18)); d.rectangle([0,HEAD-6,W,HEAD],fill=TEAL)
    t1=spec.get('title','CHARACTER SHEET'); d.text((M,26),t1,font=F(74),fill=TXT)
    d.text((M+d.textlength(t1,font=F(74))+50,26),spec.get('headline',''),font=F(74),fill=TEAL)
    d.text((M,116),spec.get('subtitle',''),font=F(32,False),fill=MUT)
    y=HEAD+G; pnum=0
    for r,h,pw,ch in rows:
        x=M; pi=0
        for it in r['items']:
            if it['type']=='panel':
                w=pw[pi]; pi+=1; pnum+=1
                d.rounded_rectangle([x,y,x+w,y+ch],radius=14,fill=CARD,outline=LINE,width=3)
                d.ellipse([x+14,y+14,x+62,y+62],fill=ORG); d.text((x+38,y+38),str(it.get('num',pnum)),font=F(30),fill=(15,19,25),anchor='mm')
                tt=it['title']; fo=F(32)
                while d.textlength(tt,font=fo)>w-90 and fo.size>18: fo=F(fo.size-2)
                d.text((x+76,y+14),tt,font=fo,fill=TXT); d.line([(x+14,y+TS-8),(x+w-14,y+TS-8)],fill=TEAL,width=3)
                im=img(it['image']).resize((w-16,h),Image.LANCZOS); sh.paste(im,(x+8,y+TS))
                d.rectangle([x+7,y+TS-1,x+w-7,y+TS+h],outline=(200,208,220),width=3)
                lg=it.get('legend','')
                for i,l in enumerate(wrap(lg,F(22,False),w-24)[:2]): d.text((x+12,y+TS+h+8+i*26),l,font=F(22,False),fill=MUT)
            else:
                w=it['_w']; d.rounded_rectangle([x,y,x+w,y+ch],radius=14,fill=CARD,outline=LINE,width=3)
                d.text((x+24,y+16),it['title'],font=F(34),fill=TEAL); d.line([(x+14,y+TS-8),(x+w-14,y+TS-8)],fill=TEAL,width=3)
                bx,by,bw,bh=x+24,y+TS+6,w-48,ch-TS-30
                if it['type']=='notes':
                    yy=by
                    for para in it['lines']:
                        for l in wrap(para,F(27,False),bw): d.text((bx,yy),l,font=F(27,False),fill=TXT); yy+=36
                        yy+=14
                elif it['type']=='scale':
                    mx=max(i['cm'] for i in it['items']); n=len(it['items']); colw=bw//n; base_y=by+bh-60; maxh=bh-110
                    d.line([(bx,base_y),(bx+bw,base_y)],fill=LINE,width=3)
                    for k,i in enumerate(it['items']):
                        bh_=int(maxh*i['cm']/mx); cx=bx+k*colw+colw//2; bwid=min(70,colw//2)
                        d.rounded_rectangle([cx-bwid//2,base_y-bh_,cx+bwid//2,base_y],radius=8,fill=ORG if i.get('hero') else (70,84,102),outline=LINE,width=2)
                        d.text((cx,base_y-bh_-24),f"{i['cm']} cm",font=F(24),fill=TXT,anchor='mm'); d.text((cx,base_y+24),i['name'],font=F(20),fill=TXT,anchor='mm')
                elif it['type']=='swatches':
                    n=len(it['items']); sz=min(150,(bw-(n-1)*16)//n)
                    for k,s_ in enumerate(it['items']):
                        c=img(s_['image']).crop(tuple(s_['crop'])); r_=1
                        cw,chh=c.size
                        if cw>chh: nw=chh; xx=(cw-nw)//2; c=c.crop((xx,0,xx+nw,chh))
                        else: nh=cw; yy=(chh-nh)//2; c=c.crop((0,yy,cw,yy+nh))
                        c=c.resize((sz,sz),Image.LANCZOS); tx=bx+k*(sz+16); d.rectangle([tx-3,by-3,tx+sz+3,by+sz+3],outline=LINE,width=3); sh.paste(c,(tx,by))
                        for j,l in enumerate(wrap(s_['name'],F(18),sz+12)): d.text((tx+sz//2,by+sz+22+20*j),l,font=F(18),fill=TXT,anchor='mm')
                elif it['type']=='palette':
                    cnt=it.get('count',8); q=img(it['image']).resize((300,300)).quantize(colors=cnt,method=Image.Quantize.MEDIANCUT).convert('RGB')
                    cols=sorted(q.getcolors(),reverse=True)[:cnt]; sz=min(110,(bw-(cnt-1)*12)//cnt)
                    for k,(c_,col) in enumerate(cols):
                        tx=bx+k*(sz+12); d.rounded_rectangle([tx,by,tx+sz,by+sz+30],radius=10,fill=col,outline=LINE,width=3)
                        d.text((tx+sz//2,by+sz+52),'#%02X%02X%02X'%col,font=F(18,False),fill=TXT,anchor='mm')
            x+=(pw[pi-1] if it['type']=='panel' else it['_w'])+G
        y+=ch+G
    os.makedirs(os.path.dirname(os.path.abspath(out)),exist_ok=True); sh.save(out); return sh.size
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('--base',required=True); ap.add_argument('--out',required=True)
    a=ap.parse_args(); print(render(json.load(open(a.spec)),a.base,a.out))
