import sys
from PIL import Image,ImageDraw
def card(w,h,path):
    im=Image.new("RGB",(w,h));px=im.load()
    d=ImageDraw.Draw(im)
    for y in range(h):
        t=y/h; d.line([(0,y),(w,y)],fill=(int(250*(1-t)+40*t),int(200*(1-t)+120*t),int(120*(1-t)+200*t)))
    s=max(w,h)//10
    for x in range(0,w,s): d.line([(x,0),(x,h)],fill=(255,255,255),width=max(1,w//300))
    for y in range(0,h,s): d.line([(0,y),(w,y)],fill=(255,255,255),width=max(1,w//300))
    r=min(w,h)//4;d.ellipse([w//2-r,h//2-r,w//2+r,h//2+r],fill=(230,60,50))
    b=max(3,w//60);d.rectangle([0,0,w-1,h-1],outline=(20,20,20),width=b)
    d.rectangle([0,0,w//5,h//12],fill=(20,160,80))  # top-left marker
    im.save(path)
if __name__=="__main__": card(int(sys.argv[1]),int(sys.argv[2]),sys.argv[3])
