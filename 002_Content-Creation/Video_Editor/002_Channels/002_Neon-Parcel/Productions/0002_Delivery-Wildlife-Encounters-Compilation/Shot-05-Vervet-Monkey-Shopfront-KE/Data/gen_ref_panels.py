import json, subprocess, sys, os, time, concurrent.futures as cf, urllib.request
sys.path.insert(0,'/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Environment-Sheet-Generation/scripts')
from image_generation import _resolve_to_public_url as up
ENV=os.path.expanduser('~/.env-secrets')
def kie(args):
    r=subprocess.run(['kie-cli']+args,capture_output=True,text=True)
    return r.stdout if r.stdout.strip() else r.stderr
COMMON=("Plain neutral light-gray studio background, even soft studio lighting, photorealistic, exactly the same individual as the reference identity image (same face, build, coloration, clothing). ONE single image showing only the requested view, no text, no labels, no borders, no watermark, no other people or animals.")
SUBJ={
 'Courier':dict(ident='Character_Sheets/Bicycle_Courier_Character_Sheet.png',
   who="the bicycle courier: an adult East African man in his late 20s-30s, average build, plain navy short-sleeve collared shirt with a chest pocket, dark trousers, black sandals, black crossbody shoulder bag, pale beige clipboard with a pen; NO logos or text anywhere",
   panels=[('01_Front','Front view',"Full-body FRONT view, standing straight, arms relaxed at his sides, facing the camera, entire body from head to sandals visible with margin around it",'3:4'),
    ('02_Side','Side profile',"Full-body RIGHT-SIDE profile view (his right side toward the camera), standing straight, entire body head to sandals visible",'3:4'),
    ('03_Back','Back view',"Full-body BACK view, standing straight, entire body head to sandals visible, showing the crossbody bag strap across his back",'3:4'),
    ('04_FullBody','Full body 3/4',"Full-body THREE-QUARTER view walking mid-stride, holding the pale beige clipboard with a pen in his RIGHT hand, entire body visible",'3:4'),
    ('05_Neutral','Neutral expression',"Head-and-shoulders portrait, neutral calm expression, looking at the camera",'1:1'),
    ('06_Effort','Focused / exertion expression',"Head-and-shoulders portrait, focused effortful expression as if pushing hard or startled and lunging, brow tense, slight sweat",'1:1'),
    ('07_Face','Face close-up',"Tight close-up of his face only, front view, skin texture and facial hair detail visible",'1:1'),
    ('08_RightHand','Right hand + forearm',"Close-up of his RIGHT hand and forearm only (as seen from the front, his right arm), relaxed open hand, navy sleeve hem visible",'1:1'),
    ('09_LeftHand','Left hand + forearm',"Close-up of his LEFT hand and forearm only, relaxed open hand, navy sleeve hem visible",'1:1'),
    ('10_Feet','Feet + footwear',"Close-up of his feet and black sandals with the lower trouser hems, standing on plain floor",'1:1'),
    ('11_Clothing','Clothing + carried items',"Close-up of the recurring items: navy collared shirt chest pocket, the black crossbody shoulder bag with its strap and buckle, and the pale beige clipboard with attached pen held against his hip",'4:3')]),
 'Monkey':dict(ident='Character_Sheets/Vervet_Monkey_Character_Sheet.png',
   who="a real wild vervet monkey (Chlorocebus pygerythrus): grey-green-tinged fur, black face with a white brow band and pale cheek fur, small dexterous black hands and feet, long tail, cat-sized body about 40-60 cm excluding tail",
   panels=[('01_Front','Front view',"FRONT view, sitting upright on all fours facing the camera, entire body visible with margin",'3:4'),
    ('02_Side','Side profile',"Full-body SIDE profile standing on all four limbs, entire body and full long tail visible",'4:3'),
    ('03_Back','Back view',"BACK view, entire body and tail visible from behind",'3:4'),
    ('04_FullBody','Full body 3/4',"Full-body THREE-QUARTER view standing on all four limbs, alert, whole tail visible",'4:3'),
    ('05_Resting','Resting pose',"Resting neutral pose, sitting relaxed with hands on its knees, tail curled on the ground",'4:3'),
    ('06_Alert','Active / alert pose',"Alert active pose, head raised, ears and eyes attentive, one hand lifted, ready to spring",'4:3'),
    ('07_EyesFace','Eyes + face close-up',"Tight close-up of the face and eyes, front view, black face, white brow band, brown eyes",'1:1'),
    ('08_Markings','Markings + coloration',"Close-up on the distinguishing markings and coloration: white brow band, black face, pale cheek fur, grey-green coat and lighter chest fur",'1:1'),
    ('09_Hands','Key feature: hands gripping a clipboard',"Close-up of its two small dexterous black hands both gripping the edge of a small pale beige clipboard with a pen attached, fingers clearly visible",'1:1'),
    ('10_FurTail','Fur + tail texture',"Close-up texture study of the fur on its shoulder and the long tail with its darker tip",'1:1'),
    ('11_Movement','Movement pose',"Movement pose: climbing up a vertical weathered rusty steel post with hands and feet gripping it, tail hanging down, whole body visible against the plain background",'3:4')])}
def run(key,names_filter=None,refs_extra=()):
    S=SUBJ[key]; ident=up(S['ident']); jobs=[]
    for fn,title,desc,ar in S['panels']:
        if names_filter and fn not in names_filter: continue
        prompt=(f"Reference image 1 is the approved identity sheet for {S['who']}. "+(f"Reference image 2 is the master front view of the same individual. " if refs_extra else '')+
                f"Generate: {desc}. {COMMON}")
        pf=f'Prompts/{key}-Sheet-Panel-{fn}-GPT-Image-2-v1.md'
        open(pf,'w').write(f"---\nmodel: gpt-image-2\nparams: image-to-image, {ar}, 2K, refs: identity sheet {S['ident']}{' + master front panel' if refs_extra else ''}\nsaved: 2026-09-20 BEFORE submission\n---\n{prompt}\n")
        args=['gpt_image_2','--prompt',prompt,'--input_urls',ident]+sum([['--input_urls',u] for u in refs_extra],[])+['--aspect_ratio',ar,'--resolution','2K','--json']
        jobs.append((fn,args))
    def go(j):
        fn,args=j
        for attempt in range(3):
            try:
                tid=json.loads(kie(args))['task_id']
                for _ in range(60):
                    time.sleep(6); st=json.loads(kie(['get_task_status','--task_id',tid,'--json']))
                    if st.get('status')=='success' and st.get('result_urls'):
                        out=f"Character_Sheets/Panels/{key}/{fn}.png"; subprocess.run(['curl','-sL','-A','AgentOS','-o',out,st['result_urls'][0]],check=True); return fn,(out if os.path.getsize(out)>10000 else None)
                    if st.get('status')=='fail': break
            except Exception as e: print('err',fn,e)
        return fn,None
    with cf.ThreadPoolExecutor(6) as ex: return list(ex.map(go,jobs))
if __name__=='__main__':
    key=sys.argv[1]; phase=sys.argv[2]
    if phase=='front':
        print(run(key,['01_Front' if key=='Courier' else '02_Side']))
    else:
        front='Character_Sheets/Panels/%s/%s.png'%(key,'01_Front' if key=='Courier' else '02_Side')
        done=[f[:-4] for f in os.listdir('Character_Sheets/Panels/'+key)]
        print(run(key,[p[0] for p in SUBJ[key]['panels'] if p[0] not in done],refs_extra=(up(front),)))
