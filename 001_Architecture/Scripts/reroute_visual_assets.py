"""
Re-route images from Visual_Assets/ to correct subfolders based on filename classification.
Also moves matching Asset Notes and updates their embed links.
"""
import os
import re
import shutil
import argparse

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
VISUAL_ASSETS = f"{WORKSPACE}/007_Resource_Library/Obsidian_Attachments/Visual_Assets"
ASSET_NOTES   = f"{WORKSPACE}/007_Resource_Library/Asset_Notes"

DESTINATIONS = {
    "Tools":        f"{WORKSPACE}/007_Resource_Library/Tools",
    "Bookmarks":    f"{WORKSPACE}/007_Resource_Library/Bookmarks",
    "Tutorials":    f"{WORKSPACE}/007_Resource_Library/Tutorials",
    "Docs":         f"{WORKSPACE}/007_Resource_Library/Docs",
    "Visual_Assets": VISUAL_ASSETS,
}

# Keyword sets — order matters (first match wins)
RULES = [
    ("Tutorials", [
        "tutorial", "how-to", "howto", "guide", "setup", "install", "course",
        "breakdown", "step-by-step", "walkthrough", "learn", "getting-started",
        "build-with", "one-click-rig", "ep3", "ep-", "irl-ep",
    ]),
    ("Bookmarks", [
        ".github", "github-com", "github.com", "awesome-",
        "repo-list", "nocode-joshua", "skilljar", "skills-sh",
        "rm-skills", "rm-skills-repo", "nano-banana-prompts.github",
        "nano-banana-prompt-library", "web-assets-generator.github",
        "awesome-claude", "marketingskills-claude", "alimpl-claude",
        "public-apis-repo",
    ]),
    ("Docs", [
        "spreadsheet", "chart", "data", "research", "stats", "report",
        "analytics", "nfl-", "nfl-game", "nfl-popular", "nfl-starts",
        "audience-trends", "studio-audience", "studio-breese",
        "selling-daily-ranking", "virality-structures",
        "travel-pitch", "travel-ugc", "travel-destinations",
        "coinbase-usdc", "reddit-usdc", "autopilot-investment",
        "sofi-personal", "nerdwallet", "bsb-alinea",
        "platinum-group", "vanadium", "troy-minerals",
    ]),
    ("Tools", [
        # AI / coding tools
        "claude-", "codex", "gemini-", "openai-", "anthropic-",
        "chatgpt-", "copilot", "n8n-", "firecrawl", "lindy-",
        "pokee-ai", "lumalabs", "hailuo", "odyssey-", "ray-video",
        "sora-", "wan-animate", "vio-wan", "genie-", "genie-world",
        "hunyuan", "tencent-", "tripo-", "tripod-ai",
        "hera-ai", "veovault", "vercept", "sim-studio",
        "boolvideo", "beeble-vfx", "neuralframes", "lucy-edit",
        "browser-use", "agentkit", "agency-agents",
        "opencore-wyzer", "wyzer-studios",
        "base-full-ai", "base44", "makesthem",
        "canvas-for-mind", "intangible-ai", "liberty-ai",
        "discout-ai", "teabie-ai", "effect-app",
        "dora-studio", "dorastudio", "rive-editor", "rive-",
        "rotato-mockup", "ditherboy",
        "pear-video", "sideo", "floodify", "swooped",
        "vochlea", "finevoice", "dj-fazio",
        "glew-ee", "social-cat", "cohley",
        "nexlev", "tubegen", "viewstats", "mozaic",
        "motionisland", "motion-island",
        "react-bits", "style-dropper",
        "promptly-ai", "propmts-chat",
        "cap-so", "chatvideopro", "jumpspeak", "keypano",
        "kyutai", "softr", "string-", "warmwind",
        "webflowgasp", "virtualthreads", "pocket-marco",
        "collabaway", "creativify", "tabiplaces",
        "world-labs", "worldlabs",
        "elevenlabs", "audius-",
        "google-vids", "google-pomelli", "google-pitch",
        "google-skills", "google-side",
        "pipedream", "publiqueapis",
        "free-virtual-conference",
        "hiring-cafe", "techapply", "yt-jobs",
        "swooped", "job-boards",
        "revamped-io",
        "ai-map-animation", "ai-video-sora",
        "ai-image-generation",
        "aicheercheung", "cheer-ai", "poormarty",
        "secret-society-animation",
        "midjourney-comic", "photo-colorization",
        "blosm-blender", "one-click-rig",
        "duckpack", "free-text-to-video",
        "antigravity-sora", "tool-motion-ai",
        "tool-taskade", "tool-tiktok-growth",
        "tiktok-ai-agent", "tiktok-higgsfield",
        "firecrawl-mcp",
        "explain-code", "claude-deep-research",
        "claude-mem-plugin", "claude-must-install",
        "claude-skills-jobs", "rm-skills",
        "skills-sh", "jobs-to-be-done-skill",
        "web-assets-generator-skill",
        "nano-banana-prompt",
        "graph-", "graphify",
        "geoguessr",
        "polaroid-gemini",
        "google-aintignawity",
        "combinator-open-source",
    ]),
    # Social media, product photos, POD, TikTok content → Visual_Assets (stay)
    ("Visual_Assets", [
        "tiktok-", "instagram-", "youtube-studio", "youtube-tool",
        "gossip-goblin", "real-life-lore", "military-youtube",
        "orenmeetsworld", "across-the-globe",
        "oren-john", "aliabdaal",
        "t-shirt", "tshirt", "dog-mom", "plant-killer",
        "powered-by-coffee", "tuesday-survival",
        "printful-eco", "print-on-demand", "print-ify",
        "clothing-brand", "aurora-print",
        "sad-dog", "funny-daycare", "police-dog",
        "security-cam", "meow-toptop",
        "soap-dispenser", "aldi-sourdough", "oxygen-naturals",
        "oxynercy", "get-it-fresh", "getitfresh",
        "western-coquette", "chinoiserie",
        "lan-xang", "nipponhomes", "modernliving",
        "solo-travel", "waves-travel",
        "paintfumestour", "aura-twitter",
        "identity-struggle", "shape-of-desire",
        "drift-away-song", "morty-sound",
        "meow-", "lofi", "virality-",
        "tiktok-viral", "tiktok-earnings",
        "tiktok-live", "tiktok-spark", "tiktok-json",
        "tiktok-your-niche", "tiktok-use-to",
        "tiktok-who-michael", "tiktok-stayviral",
        "facebook-animal", "faceless-youtube",
        "bn-post-idea", "post-ideas",
        "live-explore", "live-stem", "live-tem",
        "tive-tem", "tive-stem", "tive-explore",
        "ive-stem", "oll-lte", "eal-lte", "lte-",
        "aaa-guy", "aca-exolore",
        "brush-swatch", "themes-",
        "videos-", "workflow-", "screenshot-",
    ]),
]

IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.PNG', '.JPG', '.JPEG')


def classify(stem):
    s = stem.lower().replace('_', '-')
    for dest, keywords in RULES:
        for kw in keywords:
            if kw in s:
                return dest
    return "Visual_Assets"  # default


def move_file_and_note(filename, destination, dry_run=False):
    src_image = os.path.join(VISUAL_ASSETS, filename)
    stem = os.path.splitext(filename)[0]
    note_filename = f"{stem}.md"
    src_note = os.path.join(ASSET_NOTES, note_filename)

    dst_dir = DESTINATIONS[destination]
    dst_image = os.path.join(dst_dir, filename)
    dst_note = os.path.join(dst_dir, note_filename)

    moved = []

    if os.path.exists(src_image):
        if not dry_run:
            os.makedirs(dst_dir, exist_ok=True)
            shutil.move(src_image, dst_image)
        moved.append(f"image → {destination}/{filename}")

    if os.path.exists(src_note):
        if not dry_run:
            os.makedirs(dst_dir, exist_ok=True)
            content = open(src_note, 'r', encoding='utf-8').read()
            # Update embed link to new path (just the filename, Obsidian resolves it)
            open(dst_note, 'w', encoding='utf-8').write(content)
            os.remove(src_note)
        moved.append(f"note  → {destination}/{note_filename}")

    return moved


def main():
    parser = argparse.ArgumentParser(description="Re-route Visual_Assets images to correct subfolders.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would happen without moving anything")
    args = parser.parse_args()

    files = [f for f in os.listdir(VISUAL_ASSETS)
             if os.path.isfile(os.path.join(VISUAL_ASSETS, f))
             and f.lower().endswith(tuple(e.lower() for e in IMAGE_EXT))]

    counts = {"Tools": 0, "Bookmarks": 0, "Tutorials": 0, "Docs": 0, "Visual_Assets": 0}
    stayed = []
    moved_log = []

    for filename in sorted(files):
        stem = os.path.splitext(filename)[0]
        dest = classify(stem)
        counts[dest] += 1

        if dest == "Visual_Assets":
            stayed.append(filename)
            continue

        results = move_file_and_note(filename, dest, dry_run=args.dry_run)
        for r in results:
            moved_log.append(r)
        if args.dry_run:
            print(f"[DRY RUN] {filename} → {dest}")

    mode = "DRY RUN" if args.dry_run else "COMPLETE"
    print(f"\n=== Reroute {mode} ===")
    print(f"Total images:   {sum(counts.values())}")
    for dest, count in counts.items():
        print(f"  {dest:<14} {count}")

    if not args.dry_run and moved_log:
        print(f"\nMoved {len([l for l in moved_log if 'image' in l])} images and {len([l for l in moved_log if 'note' in l])} notes.")


if __name__ == "__main__":
    main()
