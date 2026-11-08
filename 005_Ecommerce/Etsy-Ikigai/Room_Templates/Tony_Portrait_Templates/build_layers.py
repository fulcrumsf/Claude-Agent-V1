import numpy as np, cv2, json, os, sys
from PIL import Image
import lib
def make_layers(img, q_inner, kind, mode, ring=None, ratio=None, occluder=False, outdir=".", occ_region=(-0.01,0.6,1.01,1.02), occ_v=1.01):
    """returns dict meta + writes L_*.png full-canvas layers into outdir"""
    os.makedirs(outdir,exist_ok=True)
    H,W=img.shape[:2]; w_,h_=lib.quad_dims(q_inner)
    if mode=="full":
        q_so=q_inner
        if ratio: so=(round(h_*ratio),round(h_))
        else: so=(round(w_),round(h_))
    else:
        r=ratio; sh_=0.84*h_
        if sh_*r>0.80*w_: sw=0.80*w_; sh_=sw/r
        else: sw=sh_*r
        du=(1-sw/w_)/2; dv=(1-sh_/h_)/2; dv_top=dv*0.92
        q_so=lib.sub_quad(q_inner,du,dv_top,1-du,dv_top+sh_/h_)
        so=(round(sw),round(sh_))
    side=lib.light_side(img,q_inner)
    m_in=lib.poly_mask(q_inner,W,H); m_so=lib.poly_mask(q_so,W,H)
    layers=[]
    if kind=="art" and mode=="mat":
        paper=np.ones((H,W,3),"float32")*np.float32([0.965,0.955,0.94])
        lib.save_rgba(paper,m_in,f"{outdir}/L_paper.png"); layers.append(("paper","L_paper.png"))
    if kind=="blank":
        clean,_,nbad=lib.light_from_blank(img,q_inner); light=clean
    else:
        light=lib.light_synthetic(img, q_inner if mode=="mat" else q_so, ring); nbad=0
    lm=m_in
    lib.save_rgba(light,lm,f"{outdir}/L_light.png")
    k=0.5 if kind=="blank" else 1.0
    if mode=="full":
        e=lib.edge_shadow(q_so,W,H,side,strength=tuple(s*k for s in (0.30,0.12,0.22,0.08)))
        lib.save_rgba(np.repeat(e[...,None],3,-1),m_so,f"{outdir}/L_edge.png")
    else:
        e=lib.edge_shadow(q_inner,W,H,side,strength=tuple(s*k for s in (0.30,0.12,0.22,0.08)))
        lib.save_rgba(np.repeat(e[...,None],3,-1),m_in,f"{outdir}/L_edge.png")
        b=lib.edge_shadow(q_so,W,H,side,strength=(0.22,0.06,0.16,0.05),width=0.006)
        lib.save_rgba(np.repeat(b[...,None],3,-1),m_so,f"{outdir}/L_bevel.png")
    g=lib.glass(q_inner,W,H)
    lib.save_rgba(np.ones((H,W,3),"float32"),g*m_in,f"{outdir}/L_glass.png")
    if occluder:
        hsv=cv2.cvtColor((img*255).astype("uint8"),cv2.COLOR_RGB2HSV).astype("float32")/255
        u,v=lib.uv_maps(q_inner,W,H)
        occ=(((hsv[...,1]>0.30)&(hsv[...,2]<occ_v))|(hsv[...,2]<0.42)).astype("uint8")
        occ=cv2.morphologyEx(occ,cv2.MORPH_OPEN,np.ones((3,3),"uint8"))
        occ=cv2.dilate(occ,np.ones((3,3),"uint8")).astype("float32")
        inside=lib.poly_mask(lib.sub_quad(q_inner,*occ_region),W,H)
        a=cv2.GaussianBlur(occ*inside,(0,0),0.8)
        lib.save_rgba(img,a,f"{outdir}/L_occ.png")
    lib.placeholder(so[0],so[1],f"{outdir}/placeholder.png")
    return dict(q_inner=[[round(x,2) for x in p] for p in q_inner], q_so=[[round(x,2) for x in p] for p in q_so],
                so_px=list(so), ratio=round(so[0]/so[1],4), light_from=side, kind=kind, mode=mode, ring=ring, inpainted_px=nbad)

def assemble(base_path, outdir, meta, out_psd, occluder=False, base_name="BASE (room photo)"):
    P=lambda n: os.path.abspath(f"{outdir}/{n}")
    cmd=lib.cmd
    def place(f,name,blend="Normal",op=1.0,vis=True):
        return cmd("file.placeEmbedded",{"path":P(f),"smartObject":False,"scale":100})+cmd("layer.setProps",{"name":name,"blend":blend,"opacity":op,"visible":vis})
    a=[lib.CLI,"run",base_path]+cmd("layer.setProps",{"name":base_name})
    last=base_name
    if os.path.exists(P("L_paper.png")):
        a+=place("L_paper.png","Paper (covers old sample art)")+cmd("layer.new.group",{"name":"MAT"})+cmd("layer.moveTo",{"layer":"Paper (covers old sample art)","target":"MAT","position":"into"})
        last="MAT"
    a+=cmd("layer.select",{"name":last})+cmd("file.placeEmbedded",{"path":P("placeholder.png"),"smartObject":True,"scale":100})
    a+=cmd("layer.setProps",{"name":"Place Artwork Here","blend":"Normal"})+cmd("edit.transform",{"quad":meta["q_so"]})
    sh=["Scene Light & Shadow","Frame Edge Shadow"]
    a+=place("L_light.png","Scene Light & Shadow","Multiply")+place("L_edge.png","Frame Edge Shadow","Multiply")
    if os.path.exists(P("L_bevel.png")): a+=place("L_bevel.png","Mat Bevel Shadow","Multiply"); sh.append("Mat Bevel Shadow")
    a+=cmd("layer.new.group",{"name":"SHADOWS"})
    for n in sh: a+=cmd("layer.moveTo",{"layer":n,"target":"SHADOWS","position":"into"})
    a+=cmd("layer.select",{"name":"SHADOWS"})+place("L_glass.png","Glass Sheen","Screen",0.12)
    a+=cmd("layer.new.group",{"name":"GLARE"})+cmd("layer.moveTo",{"layer":"Glass Sheen","target":"GLARE","position":"into"})
    if occluder:
        a+=cmd("layer.select",{"name":"GLARE"})+place("L_occ.png","Foreground Plant (in front of frame)")
        a+=cmd("layer.new.group",{"name":"FOREGROUND"})+cmd("layer.moveTo",{"layer":"Foreground Plant (in front of frame)","target":"FOREGROUND","position":"into"})
    a+=["--out",out_psd]
    return lib.run(a,out_psd)
