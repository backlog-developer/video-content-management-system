import os
import hashlib
import subprocess
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Directories
UPLOAD_DIR = "static/uploads"
CHUNK_DIR = "static/chunks"
THUMBNAIL_DIR = "static/thumbnails"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

# Import external processing scripts
from scripts.transcoding import transcode_video
from scripts.thumbnails import generate_thumbnail

def compute_sha256(file_path):
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    file_id = request.args.get("file_id")
    chunk_index = request.args.get("chunk_index", type=int)
    total_chunks = request.args.get("total_chunks", type=int)
    expected_hash = request.args.get("expected_hash")

    if not file_id or chunk_index is None or total_chunks is None:
        return jsonify({"error": "Missing required parameters"}), 400

    chunk_file = request.files.get("chunk")
    if not chunk_file:
        return jsonify({"error": "No file chunk provided"}), 400

    chunk_folder = os.path.join(CHUNK_DIR, file_id)
    os.makedirs(chunk_folder, exist_ok=True)
    chunk_path = os.path.join(chunk_folder, f"chunk_{chunk_index}")
    chunk_file.save(chunk_path)
    
    if len(os.listdir(chunk_folder)) == total_chunks:
        final_file_path = os.path.join(UPLOAD_DIR, file_id + ".mp4")
        with open(final_file_path, "wb") as final_file:
            for i in range(total_chunks):
                with open(os.path.join(chunk_folder, f"chunk_{i}"), "rb") as cf:
                    final_file.write(cf.read())
        
        import shutil
        shutil.rmtree(chunk_folder)
        
        computed_hash = compute_sha256(final_file_path)
        if expected_hash and computed_hash != expected_hash:
            os.remove(final_file_path)
            return jsonify({"error": "File integrity check failed"}), 400
        
        output_formats = transcode_video(final_file_path)
        thumbnail_path = generate_thumbnail(final_file_path)
        
        return jsonify({
            "message": "File uploaded and processed successfully",
            "computed_hash": computed_hash,
            "output_formats": output_formats,
            "thumbnail": thumbnail_path
        }), 200
    
    return jsonify({"message": f"Chunk {chunk_index} uploaded successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
