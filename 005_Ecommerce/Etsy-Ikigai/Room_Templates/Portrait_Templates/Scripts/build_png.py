"""Authoring script (2026-11-08): builds <Scene>_Template.psd from the flat 007_For_Use scene PNGs listed in specs.py
(BASE photo, Place Artwork Here smart object with the frame quad, SHADOWS/GLARE groups). Uses snapped.json (edge-snapped
quads) from the scratch run; specs.py holds the by-eye quads.
NOTE (2026-11-08 re-org): this ran once against the OLD layout (00N_Ratio_* / 007_For_Use folders). Those files now
live in <NN_Ratio_*>/<Room_Type>/<Template>/ folders; the path table is in ../../Directory.md. Kept for reference."""
import json,os,sys,shutil
import lib,specs,build_layers as BL
F="/Users/tonymacbook2025/Documents/Agent-OS/005_Ecommerce/Etsy-Ikigai/Room_Templates/Portrait_Templates/007_For_Use/"
snapped=json.load(open("snapped.json"))

def R(x0,y0,x1,y1): return [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
manual={"BDRM_Girl_Pink_Modern_2x3.png":specs.PNG["BDRM_Girl_Pink_Modern_2x3.png"]["quad"],
        "LVRM_Japandi_Simple_ISO.png":R(1090,269,1532,894),
        "LVRM_Minimal_ISO.png":R(1218,478,1600,1125),
        "LVRM_Modern_BLue_ISO.png":R(1121,382,1607,1061)}
only=sys.argv[1:]
allmeta=json.load(open("png_meta.json")) if os.path.exists("png_meta.json") else {}
for n,s in specs.PNG.items():
    if only and n not in only: continue
    q=manual.get(n) or snapped[n]["quad"]
    stem=os.path.splitext(n)[0]; od=f"layers/{stem}"
    img=lib.load(F+n)
    meta=BL.make_layers(img,q,s["kind"],s["mode"],s.get("ring"),s.get("ratio"),s.get("occluder",False),od)
    meta["room"]=s["room"]
    # BASE must be a flat png the CLI can open; webp ok?
    base=F+n
    if n.endswith(".webp"):
        from PIL import Image; base=os.path.abspath(f"{od}/base.png"); Image.open(F+n).convert("RGB").save(base)
    out=F+stem+"_Template.psd"
    ok=BL.assemble(base,od,meta,out,s.get("occluder",False))
    meta["psd"]=out; meta["ok"]=ok; allmeta[n]=meta
    print(n,ok,meta["so_px"],meta["ratio"],meta["light_from"],"inpainted",meta["inpainted_px"])
json.dump(allmeta,open("png_meta.json","w"),indent=1)
