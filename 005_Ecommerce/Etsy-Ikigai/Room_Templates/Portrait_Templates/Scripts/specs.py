# per-PNG scene specs: quad = inner opening TL,TR,BR,BL (px, by eye from gridded zooms)
def R(x0,y0,x1,y1): return [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
PNG = {
 "BDRM-MidCentury_ISO.png":        dict(quad=R(1149,261,1571,801), kind="art", mode="full", ring="wall", room="Mid-century bedroom, cream wall, walnut nightstands, rust cushions"),
 "BDRM_Girl_Pink_Modern_2x3.png":  dict(quad=R(628,188,1248,1109), kind="art", mode="full", ring="wall", room="Dusty-pink bedroom, pink nightstand, sun streaks"),
 "BDRM_Trendy_Nuetral_4x5.png":    dict(quad=R(740,292,1101,806), kind="art", mode="full", ring="mat", room="Warm sunlit teen bedroom desk corner, oak frame + mat"),
 "BDRM_Wabi_Vertical.png":         dict(quad=R(1050,161,1598,908), kind="blank", mode="full", room="Wabi-sabi neutral bedroom, linen bed, curtains, sun diagonal"),
 "LVRM_Boho_Neautral_ISO.png":     dict(quad=R(1844,432,2708,1646), kind="art", mode="full", ring="wall", room="Soft boho-neutral living room, beige sofa, pendant, wall hoops"),
 "LVRM_Floor_ISO.png":             dict(quad=[[2653,782],[3450,782],[3477,1868],[2640,1868]], kind="art", mode="full", ring="mat", room="Large leaning floor frame, black lounge chair, sunny window"),
 "LVRM_Japandi_Simple_ISO.png":    dict(quad=R(1099,269,1532,894), kind="blank", mode="full", room="Japandi living room, linen sofa, blossom branches, wood shelves"),
 "LVRM_Japandi_Soft_Colors.png":   dict(quad=R(1526,748,2650,1951), kind="art", mode="mat", ratio=0.8, ring="wall", room="Bright Japandi living room, beams, terracotta cushions, plants"),
 "LVRM_Midcentury_Wood.png":       dict(quad=R(700,469,1268,1121), kind="art", mode="mat", ratio=0.8, ring="wall", room="Mid-century living room, walnut side tables, lamps, sunny"),
 "LVRM_Minimal_ISO.png":           dict(quad=R(1222,479,1600,1128), kind="blank", mode="mat", ratio=2/3, room="Minimal warm living room, doorway, black mushroom lamp, hard sun"),
 "LVRM_Modern_BLue_ISO.png":       dict(quad=R(1124,381,1607,1051), kind="blank", mode="full", room="Sky-blue wall living room, teal chesterfield, palms"),
 "LVRM_Modern_Blue_2x3.png":       dict(quad=R(782,336,1178,890), kind="art", mode="full", ring="mat", room="Teal-blue wall living room, teal sofa, pendant"),
 "LVRM_Modern_Cradenza_Angled_ISO.png": dict(quad=[[1321,253],[1691,199],[1691,928],[1324,928]], kind="blank", mode="full", ratio=0.707, room="Angled view, walnut credenza, vases, big leaning frame, window light", occluder=True),
 "LVRM_Modern_Dark_4x5.png":       dict(quad=R(1289,677,2027,1612), kind="art", mode="full", ring="mat", room="Dark grey wall living room, cream sofa, teal/orange cushions, lamp"),
 "LVRM_Modern_Leather_4x5.png":    dict(quad=R(821,231,1249,823), kind="art", mode="full", ring="mat", room="White wall, tan leather wingback chair, fiddle-leaf plant, black frame + mat"),
 "LVRM_Modern_Walnut.webp":        dict(quad=R(1375,857,2467,2075), kind="art", mode="mat", ratio=0.8, ring="wall", room="Sunny mid-century living room, walnut shelves, pink chair"),
 "LVRM_Modern_Walnut_5x7.png":     dict(quad=R(1815,880,2536,1915), kind="art", mode="full", ring="mat", room="Walnut console, tan leather chair, tall windows, oak frame + mat"),
 "LVRM_Victorian_Floor_ISO.png":   dict(quad=R(1157,1097,1358,1391), kind="art", mode="full", ring="mat", room="Empty Victorian panelled room, gilt frame leaning on herringbone floor"),
 "LVRM_Wabi_ISO.png":              dict(quad=R(1063,542,1514,1152), kind="blank", mode="full", room="Wabi-sabi loft, beams, brick, olive sofa, dried branches"),
}
