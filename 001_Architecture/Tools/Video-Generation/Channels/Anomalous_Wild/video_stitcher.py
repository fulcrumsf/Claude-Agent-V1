import os
import sys
import argparse
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip

def stitch_scenes(scene_directories, final_output="final_video.mp4"):
    video_clips = []
    
    # Sort scene directories
    dirs = sorted([d for d in scene_directories if os.path.isdir(d)])
    
    for d in dirs:
        vid_path = os.path.join(d, "video.mp4")
        aud_path = os.path.join(d, "audio.mp3")
        
        if not os.path.exists(vid_path):
            print(f"Skipping {d}: Missing video.mp4")
            continue
            
        vid = VideoFileClip(vid_path)
        
        if os.path.exists(aud_path):
            aud = AudioFileClip(aud_path)
            # Match lengths: if audio is longer, loop video. If video is longer, cut video to speech length.
            if aud.duration > vid.duration:
                loops = int((aud.duration // vid.duration) + 1)
                vid = concatenate_videoclips([vid] * loops).subclip(0, aud.duration)
            else:
                vid = vid.subclip(0, aud.duration)
            vid_audio = vid.audio 
            if vid_audio is not None:
                # Lower the background audio from Veo 3
                vid_audio = vid_audio.volumex(0.15)
                # Composite Veo audio + Narration
                final_audio = CompositeAudioClip([vid_audio, aud.set_duration(vid.duration)])
                vid = vid.set_audio(final_audio)
            else:
                # No Veo audio, just use narration
                vid = vid.set_audio(aud)
            
        video_clips.append(vid)
        print(f"Processed scene: {d}")
        
    if not video_clips:
        print("No valid scenes found to stitch.")
        return
        
    print("Concatenating all clips...")
    final_clip = concatenate_videoclips(video_clips, method="compose")
    final_clip.write_videofile(final_output, fps=24, codec="libx264", audio_codec="aac", logger=None)
    print(f"Final video stitched and saved to {final_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stitch video scenes into a final output")
    parser.add_argument("scenes", nargs="+", help="Path to scene directories")
    parser.add_argument("-o", "--output", default="final_video.mp4", help="Path for the output file")
    
    args = parser.parse_args()
    stitch_scenes(args.scenes, final_output=args.output)
