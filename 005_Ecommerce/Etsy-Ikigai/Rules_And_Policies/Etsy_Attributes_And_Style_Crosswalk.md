# Etsy listing attributes (wall art) and the Ikigai style crosswalk

Source: Etsy API v3 `seller-taxonomy/nodes/2078/properties` (queried 2026-11-08 with the Ikigai app). Re-pull when Etsy changes (see Etsy_Rules_Bible.md for the handbook re-pull habit). Agents: this is standing knowledge. When a design has a style, room or subject tag, look up the matching Etsy attribute here and fill it when building the draft, even when the names differ.

## Draft rule for digital downloads
Fill only attributes that apply to a file download. NEVER set the physical-print ones: Framing, Frame mat included, Frame color, Width, Height, Depth, Material, Material features, Number of pieces. (Matches the standing etsy_draft rule: no framing, depth or mat attributes.) Orientation and Aspect ratio describe the files and are fine.

## Etsy attribute values (taxonomy 2078)
- **Room (11):** Bathroom, Bedroom, Dorm, Entryway, Game room, Kids, Kitchen & dining, Laundry, Living room, Nursery, Office
- **Home style (14):** Art deco, Art nouveau, Bohemian & eclectic, Coastal & tropical, Contemporary, Country & farmhouse, Gothic, Industrial & utility, Lodge, Mid-century, Minimalist, Rustic & primitive, Southwestern, Victorian
- **Art subject (41):** Abstract & geometric, Animal, Anime & cartoon, Architecture & cityscape, Beach & tropical, Bollywood, Comics & manga, Educational, Fantasy & Sci Fi, Fashion, Flowers, Food & drink, Geography & locale, Horror & gothic, Humorous saying, Inspirational saying, Landscape & scenery, LGBTQ pride, Love & friendship, Military, Movie, Music, Nautical, Nudes, Patriotic & flags, People & portrait, Pet portrait, Phrase & saying, Plants & trees, Religious, Science & tech, Sports & fitness, Stars & celestial, Steampunk, Superhero, Travel & transportation, TV, Typography & symbols, Video game, Western & cowboy, Zodiac
- **Occasion (22):** 1st birthday, Anniversary, Baby shower, Bachelor party, Bachelorette party, Back to school, Baptism, Bar & Bat Mitzvah, Birthday, Bridal shower, Confirmation, Divorce & breakup, Engagement, First Communion, Graduation, Grief & mourning, Housewarming, LGBTQ pride, Moving, Pet loss, Retirement, Wedding
- **Holiday (22):** Christmas, Cinco de Mayo, Dia de los Muertos, Diwali, Easter, Eid, Father's Day, Halloween, Hanukkah, Holi, Independence Day, Kwanzaa, Lunar New Year, Mardi Gras, Mother's Day, New Year's, Passover, Ramadan, St Patrick's Day, Thanksgiving, Valentine's Day, Veterans Day
- **Primary color / Secondary color (19 each):** Beige, Black, Blue, Bronze, Brown, Clear, Copper, Gold, Gray, Green, Orange, Pink, Purple, Rainbow, Red, Rose gold, Silver, White, Yellow
- **Orientation (4):** Horizontal, Round, Square, Vertical
- **Aspect ratio (8):** 1:1, 1:2, 2:3, 3:4, 4:5, 5:7 (ISO ratio), 11:14, 16:9
- **Can be personalized:** Yes, No
- Physical-only (do not fill for downloads): Framing (Framed/Unframed), Frame mat included (Yes/No), Frame color, Number of pieces included (1 to 5 or more), Material, Material features (Upcycled), Width, Height, Depth.

## Ikigai shop styles (Etsy shop sections) -> Etsy attributes
Shop style vocabulary (live shop sections, 2026-11-08): Trendy, Abstract, Animals, Botanical, Food-Drink, Game Room, Japan Art, Mid Century, Minimalism, Nature, Nursery, Retro, Travel, Typography, Vintage, Beach Ocean. (Excluded as not looks: Originals, Reimagined, Photos - Travel, Frame TV Art.)

| Shop style | Etsy attribute(s) to check | Note |
|---|---|---|
| Trendy | Home style: Contemporary | closest; no exact match |
| Abstract | Art subject: Abstract & geometric | exact |
| Animals | Art subject: Animal (Pet portrait if it depicts a pet) | |
| Botanical | Art subject: Flowers, Plants & trees | |
| Food-Drink | Art subject: Food & drink | exact; Room: Kitchen & dining |
| Game Room | Room: Game room (Art subject: Video game if gaming art) | |
| Japan Art | Art subject: Landscape & scenery or Geography & locale | no Japanese Home style |
| Mid Century | Home style: Mid-century | exact |
| Minimalism | Home style: Minimalist | |
| Nature | Art subject: Landscape & scenery, Plants & trees | |
| Nursery | Room: Nursery (also Kids) | |
| Retro | Home style: Mid-century (closest) | no Retro value |
| Travel | Art subject: Travel & transportation, Geography & locale | |
| Typography | Art subject: Typography & symbols (Phrase & saying, Inspirational saying when words) | |
| Vintage | Home style: Victorian, Art deco or Art nouveau by era; else none | |
| Beach Ocean | Home style: Coastal & tropical; Art subject: Beach & tropical, Nautical | |

Tony's template-library style folders (Portrait_Templates) -> Home style: Japandi_Minimalist -> Minimalist; Modern -> Contemporary; Boho_Colorful -> Bohemian & eclectic; Scandinavian -> Minimalist; Neutral_Aesthetic -> Minimalist or Contemporary; Rustic_Farmhouse -> Country & farmhouse; Retro_Kitchen / Retro_Arcade -> Mid-century (closest); Gamer / Mancave -> Room: Game room. Home styles with no shop style yet: Bohemian & eclectic, Country & farmhouse, Coastal & tropical (via Beach Ocean), Art deco, Gothic, Industrial, Lodge, Rustic, Southwestern, Victorian.

## Room pick rule (Tony, 2026-11-08)
- The room check boxes Tony picks in the Portal must come from Etsy's Room list above (so the Etsy Room attribute can be filled at upload).
- Mockup rooms themselves are NOT limited to that list: Creative Space, Hallway and similar are fine as mockup scenes when the art suits them. Hallway counts as Entryway for the attribute.
- Our template room folders -> Etsy Room: Living_Rooms -> Living room; Bedroom -> Bedroom; Bathroom -> Bathroom; Kitchen_Bar -> Kitchen & dining; Office -> Office; GameRooms_Mancave -> Game room; Kids_Nursery -> Nursery (and Kids); Creative_Space -> none. Etsy rooms with no template folder yet: Dorm, Entryway (Hallway), Laundry.
