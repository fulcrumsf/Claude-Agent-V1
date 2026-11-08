"""Authoring script (2026-11-08) for Tony_Portrait_Templates: backs up each PSD as Original_<name>.psd, renames the art
smart object to 'Place Artwork Here' (deleting duplicate/hidden leftover art SOs), and converts Rectangle 1 shape slots
into smart objects with SHADOWS/GLARE layer groups. Ran from a scratch dir (paths orig/ and layers/ are relative to it).
Helpers: lib.py, build_layers.py. Re-running it is safe: backups are never overwritten."""
import os,sys,json,shutil,subprocess
import lib,build_layers as BL
T="/Users/tonymacbook2025/Documents/Agent-OS/005_Ecommerce/Etsy-Ikigai/Room_Templates/Tony_Portrait_Templates/"
C=lib.cmd
def R(x,y,w,h): return [[x,y],[x+w,y],[x+w,y+h],[x,y+h]]
RENAME={ # path: (list of layer ids to delete in the Original, (name, occurrence) of the art SO)
 "001_Ratio_ISO/001_Living_Rooms/001_Japandi_Minimalist/001_Walnut_LVRM_ISO.psd":([8],("IMAGE HERE",None)),
 "001_Ratio_ISO/001_Living_Rooms/002_Modern/Modern_Moody_Beige.psd":([],("Place Art",None)),
 "001_Ratio_ISO/001_Living_Rooms/003_Boho_Colorful/001_Colorful_LVRM_ISO.psd":([4],("IMAGE HERE",None)),
 "001_Ratio_ISO/001_Living_Rooms/003_Boho_Colorful/002_TealTiki_LVRM_ISO.psd":([],("IMAGE HERE",None)),
 "001_Ratio_ISO/004_Kitchen_Bar/001_Food_and_Drink/001_BC_Teal_Closeup.psd":([],("Rectangle 1",None)),
 "001_Ratio_ISO/004_Kitchen_Bar/001_Food_and_Drink/003_BC_White_Bar_Cart.psd":([],("Image Here",None)),
 "001_Ratio_ISO/006_GameRooms_Mancave/001_Gamer/Game_Room_ISO.psd":([],("Rectangle 1",None)),
 "003_Ratio_3x4/001_Living_Rooms/002_Modern/LVRM_Modern_Color_3x4.psd":([],("PLACE IMAGE HERE",None)),
 "003_Ratio_3x4/001_Living_Rooms/002_Modern/LVRM_Walnut_Beige_3x4.psd":([4],("PLACE IMAGE HERE",None)),
 "003_Ratio_3x4/001_Living_Rooms/003_Boho_Colorful/LVRM_Colorful_3x4.psd":([],("PLACE IMAGE HERE",None)),
 "004_Ratio_4x5/001_Living_Rooms/001_Japandi_Minimalist/LVRM_Gray_Japandi_4x5.psd":([],("PLACE IMAGE HERE",None)),
 "004_Ratio_4x5/001_Living_Rooms/001_Japandi_Minimalist/LVRM_Mint_Japandi_4x5.psd":([],("PLACE IMAGE HERE",None)),
 "004_Ratio_4x5/001_Living_Rooms/002_Modern/LVRM_Walnut_Modern_4x5.psd":([],("PLACE IMAGE HERE",None)),
 "004_Ratio_4x5/001_Living_Rooms/002_Modern/LVRM_Beige_4x5.psd":([],("Place Art Here",None)),
}
SHAPE={ # path: (bounds, kind, ring, render key, occluder region)
 "001_Ratio_ISO/004_Kitchen_Bar/001_Food_and_Drink/002_BC_Teal_ISO.psd":([2426,393,925,1198],"blank",None,"002_BC_Teal_ISO",None),
 "003_Ratio_3x4/004_Kitchen_Bar/Barcart_Green_Gold_3x4.psd":([2439,426,872,1139],"blank",None,"Barcart_Green_Gold_3x4",None),
 "007_For_Use/BDRM_Japandi_Beige_4x5.psd":([1045,466,497,660],"blank",None,"BDRM_Japandi_Beige_4x5",None),
 "007_For_Use/BDRM_Girl_Peach_Trendy_2x3.psd":([632,267,598,861],"art","wall","BDRM_Girl_Peach_Trendy_2x3",None),
 "007_For_Use/BDRM_Girl_Pink_4x5.psd":([634,368,613,814],"art","wall","BDRM_Girl_Pink_4x5",None),
 "007_For_Use/BDRM_Girl_Pink_Anime_4x5.psd":([624,288,615,803],"art","wall","BDRM_Girl_Pink_Anime_4x5",None),
 "007_For_Use/LVRM_Modern_Nook_4x5.psd":([1328,449,1275,1486],"art","inner","LVRM_Modern_Nook_4x5",(0.93,0.9,1.01,1.02)),
 "007_For_Use/LVRM_Trendy_Girl_4x5.psd":([970,235,598,744],"art","wall","LVRM_Trendy_Girl_4x5",None),
 "007_For_Use/LVRM_Trendy_Girl_5x7.psd":([1028,165,539,725],"art","wall","LVRM_Trendy_Girl_5x7",None),
 "007_For_Use/Multiple_Frames/LVRM_Midcentury_Walnut_2x3.psd":([2080,1016,697,1071],"art","wall","LVRM_Midcentury_Walnut_2x3",None),
}
def backup(rel):
    p=T+rel; d,b=os.path.split(p); o=os.path.join(d,"Original_"+b)
    if not os.path.exists(o): shutil.copy2(p,o)
    return o,p
def do_rename(rel):
    dels,(nm,occ)=RENAME[rel]; o,p=backup(rel)
    sel={"name":nm}
    if occ is not None: sel["occurrence"]=occ
    a=[lib.CLI,"run",o]+sum([C("layer.select",{"layer":i})+C("layer.delete") for i in dels],[])+C("layer.select",sel)+C("layer.setProps",{"name":"Place Artwork Here"})+["--out",p]
    return lib.run(a,rel)
def do_shape(rel):
    (x,y,w,h),kind,ring,key,occ=SHAPE[rel]; o,p=backup(rel)
    img=lib.load(f"orig/{key}.png"); q=R(x,y,w,h); od=os.path.abspath(f"layers/{key}")
    meta=BL.make_layers(img,q,kind,"full",ring,None,bool(occ),od,occ or (0,0,1,1),occ_v=0.62)
    P=lambda n: f"{od}/{n}"
    def place(f,name,blend="Normal",op=1.0):
        return C("file.placeEmbedded",{"path":P(f),"smartObject":False,"scale":100})+C("layer.setProps",{"name":name,"blend":blend,"opacity":op,"visible":True})
    a=[lib.CLI,"run",o]+C("layer.select",{"name":"Rectangle 1"})+C("layer.smartObjects.convertToSmartObject")
    a+=C("layer.setProps",{"name":"Place Artwork Here","blend":"Normal"})+C("layer.smartObjects.replaceContents",{"path":P("placeholder.png")})
    a+=place("L_light.png","Scene Light & Shadow","Multiply")+place("L_edge.png","Frame Edge Shadow","Multiply")
    a+=C("layer.new.group",{"name":"SHADOWS"})
    for n in ("Scene Light & Shadow","Frame Edge Shadow"): a+=C("layer.moveTo",{"layer":n,"target":"SHADOWS","position":"into"})
    a+=C("layer.select",{"name":"SHADOWS"})+place("L_glass.png","Glass Sheen","Screen",0.12)
    a+=C("layer.new.group",{"name":"GLARE"})+C("layer.moveTo",{"layer":"Glass Sheen","target":"GLARE","position":"into"})
    if occ:
        a+=C("layer.select",{"name":"GLARE"})+place("L_occ.png","Foreground Plant (in front of frame)")
        a+=C("layer.new.group",{"name":"FOREGROUND"})+C("layer.moveTo",{"layer":"Foreground Plant (in front of frame)","target":"FOREGROUND","position":"into"})
    a+=["--out",p]
    ok=lib.run(a,rel); meta["ok"]=ok; return meta
if __name__=="__main__" and len(sys.argv)>1:
    for rel in sys.argv[1:]: print(do_shape(rel)["ok"])
elif __name__=="__main__":
    out={}
    for rel in RENAME: out[rel]=do_rename(rel); print("R",rel,out[rel])
    for rel in SHAPE: m=do_shape(rel); out[rel]=m["ok"]; print("S",rel,m["ok"],m["so_px"],m["light_from"])
