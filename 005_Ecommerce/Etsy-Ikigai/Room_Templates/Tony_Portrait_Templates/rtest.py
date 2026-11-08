import sys,os,json,subprocess,numpy as np
from PIL import Image
import lib,testcard
OUT="renders"; os.makedirs(OUT,exist_ok=True)
def so_size(psd):
    p=os.path.abspath(f"{OUT}/_exp.png")
    r=subprocess.run([lib.CLI,"run",psd]+lib.cmd("layer.select",{"name":"Place Artwork Here"})+lib.cmd("layer.smartObjects.exportContents",{"path":p}),capture_output=True,text=True)
    if r.returncode: return None
    return Image.open(p).size
def render(psd,art,out):
    return lib.run([lib.CLI,"run",psd]+lib.cmd("layer.select",{"name":"Place Artwork Here"})+lib.cmd("layer.smartObjects.replaceContents",{"path":os.path.abspath(art)})+["--out",out],psd)
def measure(psd,key):
    w,h=so_size(psd)
    Image.new("RGB",(w,h),(0,0,0)).save(f"{OUT}/_k.png"); Image.new("RGB",(w,h),(255,255,255)).save(f"{OUT}/_w.png")
    render(psd,f"{OUT}/_k.png",f"{OUT}/_rk.png"); render(psd,f"{OUT}/_w.png",f"{OUT}/_rw.png")
    a=np.asarray(Image.open(f"{OUT}/_rk.png").convert("L")).astype(int); b=np.asarray(Image.open(f"{OUT}/_rw.png").convert("L")).astype(int)
    m=(b-a)>40; ys,xs=np.where(m)
    # visible art box: use robust percentiles
    x0,x1=np.percentile(xs,[0.5,99.5]); y0,y1=np.percentile(ys,[0.5,99.5])
    testcard.card(w,h,f"{OUT}/_tc.png"); render(psd,f"{OUT}/_tc.png",f"{OUT}/{key}.png")
    return dict(so_px=[w,h],so_ratio=round(w/h,3),vis_box=[int(x0),int(y0),int(x1-x0),int(y1-y0)],vis_ratio=round((x1-x0)/(y1-y0),3),vis_px=int(m.sum()))
if __name__=="__main__":
    res={}
    for psd in sys.argv[1:]:
        k=os.path.basename(psd)[:-4]; res[k]=measure(psd,k); print(k,res[k])
    old=json.load(open("measure.json")) if os.path.exists("measure.json") else {}
    old.update(res); json.dump(old,open("measure.json","w"),indent=1)
