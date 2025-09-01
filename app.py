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
    patch_cmd = [
        "java", "-jar", str(JAR_PATH),
        "-m", str(core_path),  # mapping/core (embed modules)
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
    return send_file(
        str(result_apk), 
        download_name="PatchedSnapchat.apk", 
        as_attachment=True, 
        mimetype="application/vnd.android.package-archive"
    )

@app.route('/patch_nomod', methods=['POST'])
def patch_nomod():
    # Validate inputs (only need apk)
    if 'apk' not in request.files:
        return "Missing form part 'apk'", 400
    if not JAR_PATH.exists():
        return f"lspatch.jar not found at {JAR_PATH}", 500
    apk = request.files['apk']
    temp_id = str(uuid.uuid4())
    temp_folder = Path("/tmp") / temp_id
    temp_folder.mkdir(parents=True, exist_ok=True)
    apk_path = temp_folder / "snapchat.apk"
    apk.save(str(apk_path))
    # No -m argument, just patch the APK with no modules embedded
    patch_cmd = [
        "java", "-jar", str(JAR_PATH),
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
    result_apk = None
    for fname in os.listdir(str(temp_folder)):
        if fname.endswith("-lspatched.apk"):
            result_apk = temp_folder / fname
            break
    if proc.returncode != 0 or result_apk is None or not result_apk.exists():
        stdout = proc.stdout.decode("utf-8", errors="ignore") if proc.stdout else ""
        stderr = proc.stderr.decode("utf-8", errors="ignore") if proc.stderr else ""
        return (
            "<h3>Patching without modules failed</h3>"
            f"<pre>{stdout[:5000]}</pre><br><pre>{stderr[:5000]}</pre>",
            400,
        )
    return send_file(
        str(result_apk), 
        download_name="PatchedSnapchatNoMods.apk",
        as_attachment=True,
        mimetype="application/vnd.android.package-archive"
    )

@app.route("/", methods=["GET"])
def root():
    return "<b>Patch server is running!</b>"

if __name__ == "__main__":
    # Render: bind to 0.0.0.0 and use PORT env or 10000 default
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
