import argparse
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

ANALYSIS_PROMPT = """
Analyze this video in detail for the purpose of recreating its visual style, humor, and camera work using AI video generation tools.

Please provide a structured analysis covering:

## 1. OVERALL STYLE & AESTHETIC
- Visual tone (e.g., cinematic, raw/handheld, clean studio, etc.)
- Color grade (warm/cool/neutral, saturated or muted)
- Overall pacing feel

## 2. CAMERA WORK
- Primary shot types used (close-up, wide, POV, overhead, etc.)
- Camera movement patterns (static, tracking, handheld shake, zoom)
- Any notable angles or perspectives

## 3. SCENE-BY-SCENE BREAKDOWN
For each distinct scene or cut, describe:
- What is happening (action/subject)
- Camera angle and framing
- What makes this moment funny or engaging
- Approximate duration

## 4. HUMOR ANALYSIS
- What specifically makes this video funny? (timing, reaction, unexpectedness, etc.)
- Key comedic moments and why they work
- Pacing of the humor (slow build vs instant payoff)

## 5. SUBJECT BEHAVIOR
- How is the main subject (e.g., cat) behaving?
- Key expressions, movements, or reactions that drive the comedy
- Any physical comedy patterns

## 6. LIGHTING & ENVIRONMENT
- Indoor/outdoor, natural/artificial light
- Background/setting details
- Depth of field usage

## 7. PROMPT RECREATION GUIDE
Based on everything above, write 3 example Veo 3.1 text-to-video prompts that would recreate the STYLE and HUMOR of this video. Format each prompt for 9:16 vertical video, 3 seconds, using the prompt structure from: detailed subject description + action/behavior + camera direction + lighting + atmosphere.
"""

def analyze_video(url: str, output_file: str | None = None) -> dict:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set. Add it to your .env file.")

    client = genai.Client(api_key=GEMINI_API_KEY)

    print(f"Sending video URL to Gemini for analysis: {url}")
    print("This may take 20–60 seconds...")

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=types.Content(
            parts=[
                types.Part(file_data=types.FileData(file_uri=url)),
                types.Part(text=ANALYSIS_PROMPT),
            ]
        ),
    )

    result = {
        "url": url,
        "analysis": response.text,
    }

    if output_file:
        with open(output_file, "w") as f:
            f.write("# Gemini Video Analysis\n\n")
            f.write(f"**Source:** {url}\n\n")
            f.write("---\n\n")
            f.write(response.text)
        print(f"Analysis saved to: {output_file}")
    else:
        print("\n" + "=" * 60)
        print(response.text)
        print("=" * 60)

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze a video URL using Gemini and extract style/humor details for AI video recreation."
    )
    parser.add_argument("url", help="YouTube or public video URL to analyze")
    parser.add_argument("-o", "--output", help="Optional .md file path to save the analysis", default=None)
    args = parser.parse_args()

    analyze_video(args.url, args.output)
