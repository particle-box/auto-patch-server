from flask import Flask, request, send_file, jsonify
import subprocess
import uuid
import os
from pathlib import Path

app = Flask(__name__)

# Resolve absolute path to lspatch.jar next to this app.py
HERE = Path(__file__).resolve().parent
JAR_PATH = HERE / "lspatch.jar"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/patch', methods=['POST'])
def patch():
    # Validate inputs
    if 'core' not in request.files or 'apk' not in request.files:
        return "Missing form parts 'core' and/or 'apk'", 400

    if not JAR_PATH.exists():
        return f"lspatch.jar not found at {JAR_PATH}", 500

    core = request.files['core']
    apk = request.files['apk']

    temp_id = str(uuid.uuid4())
    temp_folder = Path("/tmp") / temp_id
    temp_folder.mkdir(parents=True, exist_ok=True)

    core_path = temp_folder / "core.apk"
    apk_path = temp_folder / "snapchat.apk"

    core.save(str(core_path))
    apk.save(str(apk_path))

    # Run LSPatch with absolute JAR path; work in temp folder for outputs
    patch_cmd = [
        "java", "-jar", str(JAR_PATH),
        "-m", str(core_path),
        "-f",
        "-l", "2",
        "-v",
        str(apk_path)
    ]

    proc = subprocess.run(
        patch_cmd,
        cwd=str(temp_folder),
        capture_output=True
    )

    # Find produced patched APK (LSPatch naming ends with -lspatched.apk)
    result_apk = None
    for fname in os.listdir(str(temp_folder)):
        if fname.endswith("-lspatched.apk"):
            result_apk = temp_folder / fname
            break

    if proc.returncode != 0 or result_apk is None or not result_apk.exists():
        stdout = proc.stdout.decode("utf-8", errors="ignore") if proc.stdout else ""
        stderr = proc.stderr.decode("utf-8", errors="ignore") if proc.stderr else ""
        return (
            "<h3>Patching failed</h3>"
            f"<pre>{stdout[:5000]}</pre><br><pre>{stderr[:5000]}</pre>",
            400,
        )

    return send_file(str(result_apk), download_name="PatchedSnapchat.apk", as_attachment=True)

@app.route("/")
def root():
    return "<b>Patch server is running!</b>"

if __name__ == "__main__":
    # Bind to 0.0.0.0 and a known port (Render expects 0.0.0.0 and defaults to 10000)
    app.run(host="0.0.0.0", port=10000)
