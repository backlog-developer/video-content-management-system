import os
import subprocess

def transcode_video(input_path):
    """Transcodes video to multiple resolutions and formats."""
    resolutions = {"1080p": "1920x1080", "720p": "1280x720", "480p": "854x480"}
    formats = ["mp4", "webm", "mkv"]
    output_files = []
    
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = os.path.dirname(input_path)
    
    for res, size in resolutions.items():
        for fmt in formats:
            output_file = os.path.join(output_dir, f"{base_name}_{res}.{fmt}")
            command = [
                "ffmpeg", "-i", input_path, "-vf", f"scale={size}",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23", output_file
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            output_files.append(output_file)
    
    return output_files
