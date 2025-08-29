from flask import Flask, request, send_file
import subprocess
import uuid
import os

app = Flask(__name__)

@app.route('/patch', methods=['POST'])
def patch():
    core = request.files['core']
    apk = request.files['apk']

    temp_id = str(uuid.uuid4())
    temp_folder = f"/tmp/{temp_id}"
    os.makedirs(temp_folder, exist_ok=True)

    core_path = os.path.join(temp_folder, "core.apk")
    apk_path = os.path.join(temp_folder, "snapchat.apk")
    core.save(core_path)
    apk.save(apk_path)

    patch_cmd = [
    "java", "-jar", "lspatch.jar",
    "-m", core_path,
    "-f",
    "-l", "2",
    "-v",
    apk_path
    ]
    
    proc = subprocess.run(patch_cmd, cwd=temp_folder, capture_output=True)

    result_apk = None
    for fname in os.listdir(temp_folder):
        if fname.endswith("-lspatched.apk"):
            result_apk = os.path.join(temp_folder, fname)
            break

    if proc.returncode != 0 or not result_apk or not os.path.exists(result_apk):
        return (
            "<h3>Patching failed</h3><pre>{}</pre><br><pre>{}</pre>".format(
                proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8")
            ),
            400,
        )

    return send_file(result_apk, download_name="PatchedSnapchat.apk", as_attachment=True)

@app.route("/")
def root():
    return "<b>Patch server is running!</b>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
