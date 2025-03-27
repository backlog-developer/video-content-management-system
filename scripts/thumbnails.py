import os
import subprocess

def generate_thumbnail(video_path, filename):
    base_name = os.path.splitext(filename)[0]
    output_dir = "static/thumbnails"
    os.makedirs(output_dir, exist_ok=True)
    
    thumbnail_path = f"{output_dir}/{base_name}.jpg"
    command = [
        "ffmpeg", "-i", video_path, "-ss", "00:00:05", "-vframes", "1", thumbnail_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return thumbnail_path
