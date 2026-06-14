"""Scan ChatGPT export conversations and write a keyword-based theme report.

Run:
    python3 001_Architecture/Scripts/phase1_theme_discovery.py
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


WORKSPACE_ROOT = Path("/Users/tonymacbook2025/Documents/Agent-OS")
HISTORY_DIR = WORKSPACE_ROOT / "007_Resource_Library" / "OpenAI_History"
REPORT_PATH = HISTORY_DIR / "ChatGPT_Theme_Report.md"

THEME_RULES = [
    (
        "POD / Print-on-Demand",
        [
            r"\bprint[- ]?on[- ]?demand\b",
            r"\bpod\b",
            r"\btee(s| shirt|shirt)\b",
            r"\bt[- ]?shirt(s)?\b",
            r"\bhoodie(s)?\b",
            r"\bmerch\b",
            r"\bredbubble\b",
            r"\bzazzle\b",
            r"\bmockup(s)?\b",
            r"\bsweatshirt(s)?\b",
            r"\bapparel\b",
            r"\bsticker(s)?\b",
            r"\btote bag(s)?\b",
            r"\bwall art\b",
            r"\bbella canvas\b",
            r"\bcomfort colors\b",
            r"\bgildan\b",
            r"\bideogram\b",
            r"\bprintful\b",
            r"\bprintify\b",
            r"\bspreadshirt\b",
            r"\blegging(s)?\b",
        ],
    ),
    (
        "Video Production / Scripting",
        [
            r"\bshot list\b",
            r"\bscript\b",
            r"\bnarrat(or|ion|ive)?\b",
            r"\bhook\b",
            r"\bvoiceover\b",
            r"\bvoice over\b",
            r"\bscene(s)?\b",
            r"\bstoryboard\b",
            r"\bsubtitle(s)?\b",
            r"\btranscript\b",
            r"\bsrt\b",
            r"\b\d+ seconds?\b",
            r"\bread out loud\b",
            r"\breading time\b",
            r"\bclip(s)?\b",
            r"\bfootage\b",
            r"\bremot?ion\b",
            r"\bvideo prompt(s)?\b",
            r"\bimage prompt(s)?\b",
        ],
    ),
    (
        "Content Strategy / YouTube",
        [
            r"\byoutube\b",
            r"\bthumbnail(s)?\b",
            r"\bcontent strategy\b",
            r"\bcontent calendar\b",
            r"\bvideo ideas?\b",
            r"\bviral\b",
            r"\btiktok\b",
            r"\breels?\b",
            r"\bhashtag(s)?\b",
            r"\bcaption(s)?\b",
            r"\bchannel\b",
            r"\bsubscriber(s)?\b",
            r"\bviews?\b",
            r"\bseo title\b",
            r"\bevergreen\b",
            r"\bsocial media\b",
            r"\binstagram\b",
            r"\bpinterest\b",
        ],
    ),
    (
        "Coding / Development",
        [
            r"\bpython\b",
            r"\bjavascript\b",
            r"\btypescript\b",
            r"\breact\b",
            r"\bnext\.?js\b",
            r"\bapi\b",
            r"\bdeveloper\b",
            r"\bprogramming\b",
            r"\bdebug(ging)?\b",
            r"\bbug(s)?\b",
            r"\bcode\b",
            r"\bsoftware\b",
            r"\bgithub\b",
            r"\bfunction\b",
            r"\bscript(ing)?\b",
            r"\bdatabase\b",
            r"\bsupabase\b",
            r"\bnode\.?js\b",
        ],
    ),
    (
        "Business / Tax / Finance",
        [
            r"\btax(es)?\b",
            r"\birs\b",
            r"\baccounting\b",
            r"\bbookkeeping\b",
            r"\bfinance\b",
            r"\binvoice(s)?\b",
            r"\bexpense(s)?\b",
            r"\brevenue\b",
            r"\bprofit\b",
            r"\bllc\b",
            r"\b1099\b",
            r"\bw-?2\b",
            r"\bwithholding\b",
            r"\bpayment(s)?\b",
            r"\bclass action\b",
            r"\bpayroll\b",
            r"\bcrypto(currency)?\b",
            r"\bbitcoin\b",
            r"\bethereum\b",
            r"\bstock(s)?\b",
            r"\binvest(ing|ment)?\b",
            r"\bmonetiz(e|ing|ation)\b",
            r"\bmake money\b",
            r"\b\$\d+[k]?\b",
        ],
    ),
    (
        "Travel / Lifestyle",
        [
            r"\btravel\b",
            r"\bnightlife\b",
            r"\btrip\b",
            r"\bitinerary\b",
            r"\bflight(s)?\b",
            r"\bhotel(s)?\b",
            r"\bvacation\b",
            r"\bthings? to do\b",
            r"\bwhere to go\b",
            r"\brestaurant(s)?\b",
            r"\blifestyle\b",
            r"\bwhere to stay\b",
            r"\bdaytrip\b",
            r"\bday trip\b",
            r"\bbangkok\b",
            r"\bthailand\b",
            r"\bbudapest\b",
            r"\bvietnam\b",
            r"\bcambodia\b",
            r"\basia\b",
            r"\beurope\b",
            r"\brome\b",
            r"\bportugal\b",
            r"\bchiang mai\b",
            r"\bphuket\b",
            r"\bbali\b",
            r"\bsingapore\b",
            r"\bjamaica\b",
            r"\bmexico\b",
            r"\bcanada\b",
            r"\bbanff\b",
            r"\blas vegas\b",
            r"\bnab 20\d\d\b",
            r"\bairbnb\b",
            r"\bbackpack(ing)?\b",
            r"\bexpat\b",
            r"\bnomad\b",
            r"\bfood tour\b",
            r"\bstreet food\b",
            r"\bkoh samui\b",
            r"\bkoh (lanta|tao|phangan)\b",
            r"\bpattaya\b",
            r"\bmyanmar\b",
            r"\bphilippines?\b",
            r"\bindonesia\b",
            r"\bmalaysia\b",
            r"\bjapan\b",
            r"\btokyo\b",
            r"\bkyoto\b",
            r"\bkorea\b",
            r"\bseoul\b",
            r"\bcroatia\b",
            r"\bgreece\b",
            r"\bspain\b",
            r"\bparis\b",
            r"\bitalian?\b",
            r"\bprag?ue\b",
            r"\bwarsaw\b",
            r"\bpoland\b",
            r"\bbali\b",
            r"\blisbon\b",
            r"\bvilla rental\b",
            r"\bhostel\b",
            r"\bairport\b",
            r"\btransit\b",
        ],
    ),
    (
        "Personal Health",
        [
            r"\bhealth\b",
            r"\bfitness\b",
            r"\bworkout(s)?\b",
            r"\bsleep\b",
            r"\bsupplement(s)?\b",
            r"\bdiet\b",
            r"\bnutrition\b",
            r"\bmeditation\b",
            r"\banxiety\b",
            r"\bwellness\b",
            r"\blung\b",
            r"\bbrain health\b",
            r"\bmental health\b",
            r"\bexercise\b",
        ],
    ),
    (
        "Gambling / Vegas",
        [
            r"\bcasino\b",
            r"\bblackjack\b",
            r"\bpoker\b",
            r"\broulette\b",
            r"\bgambling\b",
            r"\bbetting\b",
            r"\bsportsbook\b",
            r"\bprop bet(s)?\b",
            r"\bodds\b",
            r"\bwager(s)?\b",
        ],
    ),
    (
        "AI / Agents / Automation",
        [
            r"\bchatgpt\b",
            r"\bgpt\b",
            r"\bllm\b",
            r"\bagent(s|ic)?\b",
            r"\bautomation\b",
            r"\bworkflow(s)?\b",
            r"\bmcp\b",
            r"\bprompt engineering\b",
            r"\bopenai\b",
            r"\bclaude\b",
            r"\banthropic\b",
            r"\bn8n\b",
            r"\bmake\.com\b",
            r"\bzapier\b",
            r"\bai tool(s)?\b",
            r"\bai model(s)?\b",
            r"\bfact[- ]?check(ing)?\b",
            r"\bai script\b",
        ],
    ),
    (
        "Image Generation / Design",
        [
            r"\bimage generation\b",
            r"\bdall[- ]?e\b",
            r"\bmidjourney\b",
            r"\bphotoshop\b",
            r"\bdesign\b",
            r"\blogo\b",
            r"\bposter(s)?\b",
            r"\bbrand(ing)?\b",
            r"\billustration(s)?\b",
            r"\bcanva\b",
            r"\bflatlay\b",
            r"\b4k\b",
            r"\b8k\b",
            r"\benhance\b",
            r"\bresize\b",
            r"\bartwork\b",
            r"\bcollage\b",
            r"\bartistic\b",
            r"\brender(ing)?\b",
            r"\bprompt(s)?\b",
            r"\bai art\b",
            r"\bgenerat(e|ed|ing) image\b",
            r"\bcreate (in |an? )?(image|photo|picture|art)\b",
            r"\bvector\b",
            r"\bsvg\b",
            r"\bextract text\b",
            r"\balt text\b",
            r"\bstyle(d)?\b",
            r"\baesthetic\b",
            r"\bcinematic\b",
            r"\bclose[- ]?up\b",
            r"\bwarrior\b",
            r"\bportrait\b",
            r"\babstract\b",
            r"\bcolor(s)? (psychology|scheme|palette)\b",
            r"\bcolor psychology\b",
            r"\bhumor(ous)?\b",
            r"\bquote\b",
            r"\boverlay\b",
        ],
    ),
    (
        "Ecommerce / Etsy",
        [
            r"\betsy\b",
            r"\bshopify\b",
            r"\becommerce\b",
            r"\blisting(s)?\b",
            r"\bproduct description\b",
            r"\binventory\b",
            r"\bconversion rate\b",
            r"\bshipping policy\b",
            r"\breturn policy\b",
            r"\bseller\b",
            r"\bshop\b",
            r"\bdigital download\b",
            r"\bgumroad\b",
            r"\bamazon\b",
            r"\bkdp\b",
            r"\bmerch on demand\b",
        ],
    ),
    (
        "Marketing / Ads",
        [
            r"\bmarketing\b",
            r"\bads?\b",
            r"\bseo\b",
            r"\bfunnel\b",
            r"\bcampaign\b",
            r"\blanding page\b",
            r"\bcopywriting\b",
            r"\bconversion rate\b",
            r"\blead(s)?\b",
            r"\bemail list\b",
            r"\baffiliate\b",
            r"\bpaid ad(s)?\b",
            r"\bppc\b",
            r"\bgoogle ad(s)?\b",
        ],
    ),
    (
        "Writing / Copy",
        [
            r"\bwrite\b",
            r"\bwriting\b",
            r"\brewrite\b",
            r"\bheadline(s)?\b",
            r"\bnewsletter\b",
            r"\bemail\b",
            r"\bblog\b",
            r"\barticle\b",
            r"\bessay\b",
            r"\bcaption\b",
            r"\bbio\b",
            r"\bprivacy policy\b",
            r"\babout (page|us|me)\b",
            r"\bcopyedit\b",
            r"\bgrammar\b",
            r"\btranslat(e|ion)\b",
            r"\brap\b",
            r"\blyric(s)?\b",
            r"\bsong\b",
            r"\bpoem\b",
            r"\bstory\b",
            r"\bfiction\b",
        ],
    ),
    (
        "Career / Productivity",
        [
            r"\bcv\b",
            r"\bresume\b",
            r"\binterview\b",
            r"\bjob\b",
            r"\bcareer\b",
            r"\bproductivity\b",
            r"\bgoal(s)?\b",
            r"\bschedule\b",
            r"\btime management\b",
            r"\borganize\b",
            r"\bsystem(s)?\b",
        ],
    ),
    (
        "Legal / Compliance",
        [
            r"\blegal\b",
            r"\bcontract\b",
            r"\bcompliance\b",
            r"\bpolicy\b",
            r"\blaw\b",
            r"\bagreement\b",
            r"\bterms of service\b",
            r"\bdmca\b",
            r"\bcopyright\b",
            r"\btrademark\b",
        ],
    ),
    (
        "Research / General Questions",
        [
            r"\bhistory\b",
            r"\bscience\b",
            r"\bfact(s)?\b",
            r"\bexplain\b",
            r"\bwhat is\b",
            r"\bhow does\b",
            r"\bwho (is|was|were)\b",
            r"\bncaa\b",
            r"\bnba\b",
            r"\bnfl\b",
            r"\bsports?\b",
            r"\bwikipedia\b",
            r"\bresearch\b",
            r"\bstudy\b",
            r"\bgenghis\b",
            r"\bmongol\b",
            r"\bsamurai\b",
            r"\bviking\b",
            r"\broman empire\b",
            r"\balexander\b",
            r"\bjoan of arc\b",
            r"\bottoman\b",
            r"\bmytholog\b",
            r"\bworld war\b",
            r"\bhistorical\b",
            r"\bbiograph\b",
            r"\bdocumentar\b",
            r"\bnefertiti\b",
            r"\bcleopatra\b",
            r"\bdrake\b",
            r"\bearthquake\b",
            r"\baftersh?ock\b",
            r"\bsummariz(e|ing)\b",
            r"\boverview\b",
            r"\bupdate\b",
            r"\brecent\b",
            r"\bnews\b",
            r"\bslang\b",
            r"\bhuman(ity|ities)?\b",
            r"\bphilosoph\b",
            r"\breligion\b",
            r"\bculture\b",
            r"\bcandy\b",
            r"\bfood\b",
            r"\brecipe\b",
            r"\bcooking\b",
            r"\bnoodles?\b",
            r"\bastrology\b",
            r"\bhoroscope\b",
            r"\bzodia[ck]\b",
            r"\bplanet\b",
            r"\bjupiter\b",
        ],
    ),
    (
        "Miscellaneous / One-Off Questions",
        [
            r"\bblackhead(s)?\b",
            r"\bphlegm\b",
            r"\bsebaceous\b",
            r"\bsore throat\b",
            r"\bskin care\b",
            r"\bpimple\b",
            r"\bsymptom(s)?\b",
            r"\bremedy\b",
            r"\bremedies\b",
            r"\bquake\b",
            r"\bcondo(s)?\b",
            r"\binsurance\b",
            r"\bsafetywing\b",
            r"\bcalculate\b",
            r"\bhow many days\b",
            r"\bconvert\b",
            r"\btranslat(e|ion)\b",
            r"\bcurrency\b",
            r"\bclear (the |mac |my )?terminal\b",
            r"\bshortcut(s)?\b",
            r"\bidentif(y|ication)\b",
            r"\bidentify\b",
        ],
    ),
]


def user_messages_sample(conversation, max_messages=3):
    """Return concatenated text from up to max_messages user turns."""
    mapping = conversation.get("mapping") or {}
    texts = []
    for node in mapping.values():
        message = (node or {}).get("message") or {}
        author = message.get("author") or {}
        if author.get("role") != "user":
            continue
        content = message.get("content")
        text = ""
        if isinstance(content, dict):
            parts = content.get("parts") or []
            for part in parts:
                if isinstance(part, str) and part.strip():
                    text = part.strip()
                    break
                if isinstance(part, dict):
                    candidate = part.get("text") or part.get("content")
                    if isinstance(candidate, str) and candidate.strip():
                        text = candidate.strip()
                        break
        elif isinstance(content, str):
            text = content.strip()
        if text:
            texts.append(text[:300])
        if len(texts) >= max_messages:
            break
    return " ".join(texts)[:600]


def compile_rules():
    compiled = []
    for theme, patterns in THEME_RULES:
        compiled.append((theme, [re.compile(pattern, re.IGNORECASE) for pattern in patterns]))
    return compiled


def classify(theme_rules, title, first_message):
    haystack = f"{title}\n{first_message}".lower()
    for theme, patterns in theme_rules:
        if any(pattern.search(haystack) for pattern in patterns):
            return theme
    return "Uncategorized"


def clean_title(title):
    text = str(title).replace("\r", " ").replace("\n", " ").replace('"', "'")
    return " ".join(text.split()).strip("'")


def load_conversations():
    conversations = []
    files = sorted(HISTORY_DIR.glob("conversations-*.json"))
    print(f"Found {len(files)} conversation files.")
    total = 0
    for file_index, path in enumerate(files, start=1):
        print(f"[{file_index}/{len(files)}] Reading {path.name}")
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        for conv in data:
            conversations.append(
                {
                    "title": conv.get("title") or "Untitled",
                    "create_time": conv.get("create_time"),
                    "conversation_id": conv.get("conversation_id") or conv.get("id") or "",
                    "default_model_slug": conv.get("default_model_slug") or "",
                    "first_user_message": user_messages_sample(conv),
                }
            )
        total += len(data)
        print(f"    Loaded {len(data)} conversations ({total} total).")
    return conversations


def write_report(groups):
    lines = [
        "| Theme | Count | Sample Titles |",
        "|-------|-------|---------------|",
    ]

    sortable = [
        (theme, records)
        for theme, records in groups.items()
        if theme != "Uncategorized"
    ]
    sortable.sort(key=lambda item: (-len(item[1]), item[0].lower()))

    if "Uncategorized" in groups:
        sortable.append(("Uncategorized", groups["Uncategorized"]))

    for theme, records in sortable:
        sample_titles = ", ".join(f'"{clean_title(record["title"])}"' for record in records[:3])
        lines.append(f"| {theme} | {len(records)} | {sample_titles} |")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    theme_rules = compile_rules()
    conversations = load_conversations()
    groups = defaultdict(list)

    print(f"Classifying {len(conversations)} conversations.")
    for index, conversation in enumerate(conversations, start=1):
        theme = classify(theme_rules, conversation["title"], conversation.get("first_user_message", ""))
        groups[theme].append(conversation)
        print(
            f"[{index}/{len(conversations)}] {theme}: {conversation['title']}"
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_report(groups)
    print(f"Wrote theme report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
