import numpy as np, cv2, json, subprocess, os
from PIL import Image
CLI="photocraft-cli"

def load(p): return np.asarray(Image.open(p).convert("RGB")).astype("float32")/255

def H_unit_to_img(q):
    src=np.float32([[0,0],[1,0],[1,1],[0,1]]); return cv2.getPerspectiveTransform(src,np.float32(q))

def uv_maps(q,W,H):
    Hi=np.linalg.inv(H_unit_to_img(q))
    Y,X=np.mgrid[0:H,0:W].astype("float32")
    P=np.stack([X,Y,np.ones_like(X)],-1)@Hi.T
    return P[...,0]/P[...,2],P[...,1]/P[...,2]

def poly_mask(q,W,H,aa=True):
    m=np.zeros((H,W),"uint8"); cv2.fillPoly(m,[np.int32(np.round(np.float32(q)*4))],255,lineType=cv2.LINE_AA,shift=2)
    return m.astype("float32")/255

def quad_dims(q):
    q=np.float32(q); d=lambda a,b: float(np.linalg.norm(q[a]-q[b]))
    return (d(0,1)+d(3,2))/2,(d(0,3)+d(1,2))/2

def expand(q,f):  # grow quad about its centre in unit space by fraction f of each dim
    Hm=H_unit_to_img(q); pts=np.float32([[-f,-f],[1+f,-f],[1+f,1+f],[-f,1+f]]).reshape(-1,1,2)
    return cv2.perspectiveTransform(pts,Hm).reshape(-1,2).tolist()

def sub_quad(q,u0,v0,u1,v1):
    Hm=H_unit_to_img(q); pts=np.float32([[u0,v0],[u1,v0],[u1,v1],[u0,v1]]).reshape(-1,1,2)
    return cv2.perspectiveTransform(pts,Hm).reshape(-1,2).tolist()

def snap(img,q,search=10):
    g=cv2.GaussianBlur(cv2.cvtColor((img*255).astype("uint8"),cv2.COLOR_RGB2GRAY).astype("float32"),(0,0),1.2)
    gx=cv2.Sobel(g,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(g,cv2.CV_32F,0,1,ksize=3)
    q=np.float32(q); c=q.mean(0); lines=[]; shifts=[]
    for i in range(4):
        a,b=q[i],q[(i+1)%4]; t=b-a; t/=np.linalg.norm(t); n=np.float32([-t[1],t[0]])
        if np.dot(c-a,n)<0: n=-n   # n points inward
        best=(-1,0)
        for d in range(-search,search+1):
            s=np.linspace(0.1,0.9,200)[:,None]; pts=a+(b-a)*s+n*d
            xs=np.clip(pts[:,0],0,g.shape[1]-1).astype(int); ys=np.clip(pts[:,1],0,g.shape[0]-1).astype(int)
            v=np.abs(gx[ys,xs]*n[0]+gy[ys,xs]*n[1]).mean()
            if v>best[0]: best=(v,d)
        shifts.append(best[1]); lines.append((a+n*best[1],b+n*best[1]))
    def inter(l1,l2):
        p,r=l1[0],l1[1]-l1[0]; s_,u=l2[0],l2[1]-l2[0]
        cr=lambda a,b:a[0]*b[1]-a[1]*b[0]; t=cr(s_-p,u)/cr(r,u); return (p+r*t).tolist()
    out=[inter(lines[3],lines[0]),inter(lines[0],lines[1]),inter(lines[1],lines[2]),inter(lines[2],lines[3])]
    return out,shifts

def save_rgba(rgb,a,path):
    arr=np.dstack([np.clip(rgb,0,1),np.clip(a,0,1)]); Image.fromarray((arr*255+0.5).astype("uint8"),"RGBA").save(path)

def light_from_blank(img,q):
    H,W=img.shape[:2]; m=poly_mask(q,W,H)
    x0,y0=np.int32(np.floor(np.min(q,0))); x1,y1=np.int32(np.ceil(np.max(q,0)))
    crop=(img[y0:y1+1,x0:x1+1]*255).astype("uint8")
    gray=cv2.cvtColor(crop,cv2.COLOR_RGB2GRAY).astype("float32")
    med=cv2.medianBlur(crop,31) if min(crop.shape[:2])>40 else crop
    medg=cv2.cvtColor(med,cv2.COLOR_RGB2GRAY).astype("float32")
    bad=((medg-gray)>18).astype("uint8")*255
    w_,h_=quad_dims(q); b=int(0.03*min(w_,h_))
    bad[:b]=0;bad[-b:]=0;bad[:,:b]=0;bad[:,-b:]=0
    bad=cv2.dilate(bad,np.ones((7,7),"uint8"))
    clean=cv2.inpaint(crop,bad,9,cv2.INPAINT_TELEA) if bad.any() else crop
    out=img.copy(); out[y0:y1+1,x0:x1+1]=clean.astype("float32")/255
    return out,m,int((bad>0).sum())

def light_synthetic(img,q,ring):
    """harmonic-ish fill of the light field from a ring of known-white (mat/inner) or wall pixels"""
    H,W=img.shape[:2]; w_,h_=quad_dims(q); s=min(w_,h_)
    if ring=="inner": qa,qb=sub_quad(q,0.02,0.02,0.98,0.98),sub_quad(q,0.05,0.05,0.95,0.95); outer,inner=qa,qb
    elif ring=="mat": outer,inner=expand(q,0.035),expand(q,0.008)
    else: outer,inner=expand(q,0.17),expand(q,0.11)
    ringm=(poly_mask(outer,W,H)>0.5)&~(poly_mask(inner,W,H)>0.01)
    fillm=poly_mask(outer,W,H)>0.5
    k=max(1,int(s/120))
    small=cv2.resize(img,(W//k,H//k),interpolation=cv2.INTER_AREA)
    rs=cv2.resize(ringm.astype("uint8"),(W//k,H//k),interpolation=cv2.INTER_NEAREST)>0
    fs=cv2.resize(fillm.astype("uint8"),(W//k,H//k),interpolation=cv2.INTER_NEAREST)>0
    Y=small@np.float32([0.2126,0.7152,0.0722])
    med=np.median(Y[rs]); good=rs&(Y>med*0.72)
    if ring=="wall":
        ref=np.percentile(Y[good],98); val=np.repeat((np.clip(Y/ref,0,1)*0.97)[...,None],3,-1)
    else:
        val=small.copy()
    v=np.clip(val,0,1).astype("float32"); m=good.astype("float32")
    est=np.ones_like(v)*np.float32([np.median(v[...,c][good]) for c in range(3)])
    S=s/k
    for sg in (0.6*S,0.3*S,0.15*S,0.08*S,0.04*S):
        sg=max(sg,1.0)
        den=cv2.GaussianBlur(m,(0,0),sg); num=cv2.GaussianBlur(v*m[...,None],(0,0),sg)
        nc=num/np.maximum(den,1e-6)[...,None]; conf=np.clip(den*3,0,1)[...,None]
        est=est*(1-conf)+nc*conf
    est[good]=v[good]
    unk=(fs&~good).astype("uint8")*255
    src=(np.clip(est,0,1)*255).astype("uint8")
    filled=cv2.inpaint(src,unk,max(3,int(15/k)+3),cv2.INPAINT_NS).astype("float32")/255
    if ring!="wall":   # white-ish paper/mat: normalise so its brightest reads as print white, keep 30% of its tint
        Yf=filled@np.float32([0.2126,0.7152,0.0722]); ref=np.percentile(Yf[good],95)
        g=np.clip(Yf/ref*0.96,0,1)[...,None]; tint=filled/np.maximum(Yf[...,None],1e-4)
        filled=g*(0.7+0.3*tint)
    filled=cv2.GaussianBlur(filled,(0,0),max(1.0,s/k*0.02))
    full=cv2.resize(filled,(W,H),interpolation=cv2.INTER_CUBIC)
    return np.clip(full,0,1)

def edge_shadow(q,W,H,light="left",strength=(0.30,0.22,0.22,0.10),width=0.012):
    u,v=uv_maps(q,W,H); w_,h_=quad_dims(q); s=width*min(w_,h_)
    dt,db,dl,dr=v*h_,(1-v)*h_,u*w_,(1-u)*w_
    st,sb,sl,sr=strength
    if light=="right": sl,sr=sr*0.6,sl*1.2
    elif light=="left": sl,sr=sl*1.2,sr*0.6
    sh=1-(1-st*np.exp(-np.clip(dt,0,None)/s))*(1-sb*np.exp(-np.clip(db,0,None)/s))*(1-sl*np.exp(-np.clip(dl,0,None)/s))*(1-sr*np.exp(-np.clip(dr,0,None)/s))
    return 1-sh

def glass(q,W,H):
    u,v=uv_maps(q,W,H); t=u*0.75+v*0.35
    return np.clip(0.55*np.exp(-((t-0.32)/0.16)**2)+0.25*np.exp(-((t-0.78)/0.07)**2),0,1)

def placeholder(w,h,path):
    ph=np.full((h,w,3),232,"uint8"); st=max(20,w//12); ph[:,::st]=150; ph[::st,:]=150
    Image.fromarray(ph).save(path)

def light_side(img,q):
    H,W=img.shape[:2]; w_,h_=quad_dims(q)
    L=poly_mask(expand(q,0.25),W,H)*(1-poly_mask(expand(q,0.02),W,H))
    u,_=uv_maps(q,W,H); Y=img@np.float32([0.2126,0.7152,0.0722])
    lm=(L>0.5)&(u<0); rm=(L>0.5)&(u>1)
    a=Y[lm].mean() if lm.any() else 0; b=Y[rm].mean() if rm.any() else 0
    return "left" if a>=b else "right"

def cmd(c,p=None): return ["--cmd",c,"--params",json.dumps(p or {})]

def run(args,label=""):
    r=subprocess.run(args,capture_output=True,text=True)
    errs=[l for l in (r.stdout+r.stderr).splitlines() if "error" in l.lower()]
    if r.returncode or errs: print("FAIL",label,r.returncode,errs[:5],r.stderr[-800:])
    return r.returncode==0 and not errs
