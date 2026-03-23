#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Team Docs Admin Server
Giao diện soạn thảo tài liệu nội bộ - chạy cổng 5001
"""

import re
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="admin-ui")

DOCS_DIR = Path(__file__).parent / "docs"
REPO_DIR = Path(__file__).parent

# Map section folder → label trong mkdocs.yml nav
SECTION_LABELS = {
    "system":     '"🖥️ System"',
    "network":    '"🌐 Network"',
    "sites":      '"🏢 Sites"',
    "monitoring": '"📊 Monitoring & Log"',
    "account":    '"👤 Account"',
    "security":   '"🔒 Security"',
}

# Map subsection folder → label trong mkdocs.yml nav
SUBSECTION_LABELS = {
    # system
    "server-vat-ly":   "Server vật lý",
    "proxmox":         "Proxmox VE",
    "file-server":     "File Server",
    "storage":         "Storage",
    "backup":          "Backup & Restore",
    # network
    "firewall":        "Firewall",
    "switch-core":     "Switch Core",
    "switch-distribution": "Switch Distribution",
    "switch-access":   "Switch Access",
    "controller-wifi": "Controller WiFi",
    "camera":          "Camera & Surveillance",
    "ups":             "UPS",
    # sites
    "ha-noi":          "Hà Nội",
    "da-nang":         "Đà Nẵng",
    "ho-chi-minh":     "Hồ Chí Minh",
    # monitoring
    "zabbix":          "Zabbix",
    "wazuh":           "Wazuh (SIEM)",
    "grafana":         "Grafana",
    # account
    "google":          "Google Workspace",
    "github":          "GitHub",
    "copilot":         "GitHub Copilot",
    "slack":           "Slack",
    "microsoft":       "Microsoft 365",
    # security
    "crowdstrike":     "CrowdStrike Falcon",
    "iso27001":        "ISO 27001",
    "policy":          "Security Policy",
}

# ─── API: Danh sách file ────────────────────────────────────────────────────


@app.route("/api/files")
def list_files():
    files = []
    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        rel    = md_file.relative_to(DOCS_DIR)
        parts  = rel.parts
        stem   = md_file.stem

        section    = parts[0] if len(parts) > 1 else "root"
        subsection = parts[1] if len(parts) > 2 else None

        # Tên hiển thị: index.md → tên thư mục cha
        if stem == "index" and len(parts) >= 2:
            parent_folder = parts[-2]
            display_name  = SUBSECTION_LABELS.get(parent_folder, parent_folder.replace("-", " ").title())
            is_index      = True
        else:
            display_name = stem.replace("-", " ")
            is_index     = False

        files.append({
            "path":        str(rel),
            "name":        stem,
            "displayName": display_name,
            "isIndex":     is_index,
            "section":     section,
            "subsection":  subsection,
            "display":     " / ".join(parts)
        })
    return jsonify(files)



# ─── API: Danh sách subsections của một section ─────────────────────────────

@app.route("/api/subsections")
def list_subsections():
    section = request.args.get("section", "")
    sec_dir = DOCS_DIR / section
    if not sec_dir.is_dir():
        return jsonify([])
    subs = []
    for d in sorted(sec_dir.iterdir()):
        if d.is_dir():
            subs.append({
                "folder": d.name,
                "label":  SUBSECTION_LABELS.get(d.name, d.name)
            })
    return jsonify(subs)

# ─── API: Xóa file ───────────────────────────────────────────────────────────

@app.route("/api/file", methods=["DELETE"])
def delete_file():
    path = request.args.get("path", "")
    target = DOCS_DIR / path
    if not target.exists() or not str(target.resolve()).startswith(str(DOCS_DIR.resolve())):
        return jsonify({"error": "File not found"}), 404
    if not path.endswith(".md"):
        return jsonify({"error": "Only .md files"}), 400

    target.unlink()

    # Xóa dòng khỏi mkdocs.yml
    try:
        _remove_from_nav(path)
    except Exception as e:
        print(f"Warning: could not remove from nav: {e}")

    return jsonify({"ok": True})


def _remove_from_nav(rel_path: str):
    """Xóa dòng chứa rel_path khỏi nav: trong mkdocs.yml"""
    mkdocs_file = REPO_DIR / "mkdocs.yml"
    lines = mkdocs_file.read_text(encoding="utf-8").splitlines(keepends=True)
    new_lines = [l for l in lines if rel_path not in l]
    mkdocs_file.write_text("".join(new_lines), encoding="utf-8")


# ─── API: Đổi tên / Di chuyển file ─────────────────────────────────────────

@app.route("/api/file/rename", methods=["POST"])
def rename_file():
    data     = request.json
    old_path = data.get("old_path", "").strip()
    new_path = data.get("new_path", "").strip()

    if not old_path or not new_path:
        return jsonify({"error": "Missing paths"}), 400
    if not old_path.endswith(".md") or not new_path.endswith(".md"):
        return jsonify({"error": "Only .md files"}), 400

    old_target = DOCS_DIR / old_path
    new_target = DOCS_DIR / new_path

    if not old_target.exists():
        return jsonify({"error": "Source not found"}), 404
    if new_target.exists():
        return jsonify({"error": "Destination already exists"}), 409

    new_target.parent.mkdir(parents=True, exist_ok=True)
    old_target.rename(new_target)

    # Cập nhật mkdocs.yml: thay đường dẫn cũ → mới
    try:
        mkdocs_file = REPO_DIR / "mkdocs.yml"
        content = mkdocs_file.read_text(encoding="utf-8")
        content = content.replace(old_path, new_path)
        mkdocs_file.write_text(content, encoding="utf-8")
    except Exception as e:
        print(f"Warning: could not update nav: {e}")

    return jsonify({"ok": True, "new_path": new_path})

# ─── API: Đọc file ───────────────────────────────────────────────────────────

@app.route("/api/file")
def read_file():
    path = request.args.get("path", "")
    target = DOCS_DIR / path
    if not target.exists() or not str(target.resolve()).startswith(str(DOCS_DIR.resolve())):
        return jsonify({"error": "File not found"}), 404
    return jsonify({"content": target.read_text(encoding="utf-8"), "path": path})

# ─── API: Lưu file ───────────────────────────────────────────────────────────

@app.route("/api/file", methods=["POST"])
def save_file():
    data = request.json
    path    = data.get("path", "")
    content = data.get("content", "")

    if not path or not path.endswith(".md"):
        return jsonify({"error": "Invalid path"}), 400

    target = DOCS_DIR / path
    if not str(target.resolve()).startswith(str(DOCS_DIR.resolve())):
        return jsonify({"error": "Access denied"}), 403

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return jsonify({"ok": True, "path": path})

# ─── API: Tạo file mới ───────────────────────────────────────────────────────

@app.route("/api/file/new", methods=["POST"])
def new_file():
    data       = request.json
    section    = data.get("section", "").strip()
    subsection = data.get("subsection", "").strip()   # có thể rỗng
    title      = data.get("title", "").strip()
    filename   = data.get("filename", "").strip().lower().replace(" ", "-")

    if not section or not title or not filename:
        return jsonify({"error": "Missing fields"}), 400

    if not filename.endswith(".md"):
        filename += ".md"

    # Xây đường dẫn: section/subsection/file.md hoặc section/file.md
    if subsection:
        rel_path = f"{section}/{subsection}/{filename}"
    else:
        rel_path = f"{section}/{filename}"

    target = DOCS_DIR / rel_path
    if target.exists():
        return jsonify({"error": "File already exists"}), 409

    template = f"# {title}\n\nViết nội dung ở đây...\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template, encoding="utf-8")

    # Tự động cập nhật mkdocs.yml
    try:
        _add_to_nav(section, subsection, title, rel_path)
    except Exception as e:
        print(f"Warning: could not update mkdocs.yml nav: {e}")

    return jsonify({"ok": True, "path": rel_path})


# ─── API: Upload ảnh ─────────────────────────────────────────────────────────

@app.route("/api/upload", methods=["POST"])
def upload_image():
    import uuid, mimetypes
    file = request.files.get("image")
    caller_path = request.form.get("caller_path", "")  # path của file md đang soạn

    if not file or file.filename == "":
        return jsonify({"error": "No file"}), 400

    ext = Path(file.filename).suffix.lower()
    allowed = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
    if ext not in allowed:
        return jsonify({"error": f"Không hỗ trợ định dạng {ext}"}), 400

    # Tạo tên file unique
    unique_name = f"{uuid.uuid4().hex[:10]}{ext}"
    save_path = DOCS_DIR / "assets" / "images" / unique_name
    save_path.parent.mkdir(parents=True, exist_ok=True)
    file.save(str(save_path))

    # Tính relative path từ file md đang soạn đến ảnh
    depth = len(Path(caller_path).parts) - 1  # số cấp thư mục
    prefix = "../" * depth if depth > 0 else ""
    rel_md = f"{prefix}assets/images/{unique_name}"

    return jsonify({"ok": True, "url": rel_md, "filename": unique_name})


def _add_to_nav(section: str, subsection: str, title: str, rel_path: str):
    """Thêm entry mới vào đúng vị trí trong nav: của mkdocs.yml"""
    mkdocs_file = REPO_DIR / "mkdocs.yml"
    content = mkdocs_file.read_text(encoding="utf-8")

    new_line = f"                            - {title}: {rel_path}"

    if subsection:
        # Tìm subsection label trong mkdocs.yml rồi chèn vào cuối block đó
        sub_label = SUBSECTION_LABELS.get(subsection, subsection)
        # Pattern: tìm block "  - Sub Label:\n    - ..." cho đến dòng tiếp theo ở cùng level
        pattern = rf'(                  - {re.escape(sub_label)}:.*?)(\n                  - |\n        - )'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            insert_pos = match.start(2)
            content = content[:insert_pos] + f"\n{new_line}" + content[insert_pos:]
            mkdocs_file.write_text(content, encoding="utf-8")
            return

    # Fallback: chèn vào cuối section cha
    sec_label = SECTION_LABELS.get(section)
    if not sec_label:
        return
    fallback_line = f"                  - {title}: {rel_path}"
    pattern = rf'(        - {re.escape(sec_label)}:.*?)(\n        - (?:"[^"]+"|Hướng))'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        insert_pos = match.start(2)
        content = content[:insert_pos] + f"\n{fallback_line}" + content[insert_pos:]
        mkdocs_file.write_text(content, encoding="utf-8")

# ─── API: Tạo subsection mới ─────────────────────────────────────────────────

@app.route("/api/subsection/new", methods=["POST"])
def new_subsection():
    data       = request.json
    section    = data.get("section", "").strip()
    folder     = data.get("folder", "").strip().lower().replace(" ", "-")
    label      = data.get("label", "").strip()

    if not section or not folder or not label:
        return jsonify({"error": "Missing fields"}), 400

    sub_dir = DOCS_DIR / section / folder
    if sub_dir.exists():
        return jsonify({"error": "Subsection đã tồn tại"}), 409

    # Tạo thư mục và index.md
    sub_dir.mkdir(parents=True, exist_ok=True)
    index_path = sub_dir / "index.md"
    index_path.write_text(f"# {label}\n\nViết nội dung ở đây...\n", encoding="utf-8")

    rel_path = f"{section}/{folder}/index.md"

    # Cập nhật mkdocs.yml: thêm subsection vào nav của section cha
    try:
        _add_subsection_to_nav(section, folder, label, rel_path)
    except Exception as e:
        print(f"Warning: could not update mkdocs.yml nav: {e}")

    # Cập nhật SUBSECTION_LABELS trong memory
    SUBSECTION_LABELS[folder] = label

    return jsonify({"ok": True, "path": rel_path, "folder": folder, "label": label})


def _add_subsection_to_nav(section: str, folder: str, label: str, index_path: str):
    """Thêm subsection mới vào đúng section trong nav: mkdocs.yml"""
    mkdocs_file = REPO_DIR / "mkdocs.yml"
    content = mkdocs_file.read_text(encoding="utf-8")

    sec_label = SECTION_LABELS.get(section)
    if not sec_label:
        return

    new_block = (
        f"\n                  - {label}:\n"
        f"                            - {index_path}"
    )

    # Tìm section cha rồi chèn subsection vào cuối block đó
    pattern = rf'(        - {re.escape(sec_label)}:.*?)((\n        - (?:\"[^\"]+\"|Hướng))|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        insert_pos = match.start(2) if match.group(2) else len(content)
        content = content[:insert_pos] + new_block + content[insert_pos:]
        mkdocs_file.write_text(content, encoding="utf-8")


# ─── API: Xóa subsection ─────────────────────────────────────────────────────

@app.route("/api/subsection", methods=["DELETE"])
def delete_subsection():
    section = request.args.get("section", "").strip()
    folder  = request.args.get("folder", "").strip()

    if not section or not folder:
        return jsonify({"error": "Missing section or folder"}), 400

    sub_dir = DOCS_DIR / section / folder
    if not sub_dir.is_dir():
        return jsonify({"error": "Subsection không tồn tại"}), 404

    # Kiểm tra path traversal
    if not str(sub_dir.resolve()).startswith(str(DOCS_DIR.resolve())):
        return jsonify({"error": "Access denied"}), 403

    # Xóa toàn bộ thư mục
    import shutil
    shutil.rmtree(str(sub_dir))

    # Xóa khỏi mkdocs.yml
    try:
        _remove_subsection_from_nav(section, folder)
    except Exception as e:
        print(f"Warning: could not remove subsection from nav: {e}")

    # Xóa khỏi SUBSECTION_LABELS in-memory
    SUBSECTION_LABELS.pop(folder, None)

    return jsonify({"ok": True})


def _remove_subsection_from_nav(section: str, folder: str):
    """Xóa toàn bộ block subsection (bao gồm các file con) khỏi mkdocs.yml"""
    mkdocs_file = REPO_DIR / "mkdocs.yml"
    content = mkdocs_file.read_text(encoding="utf-8")

    sub_label = SUBSECTION_LABELS.get(folder, folder)
    # Xóa tất cả dòng chứa đường dẫn section/folder/
    lines = content.splitlines(keepends=True)
    prefix = f"{section}/{folder}/"

    # Lọc bỏ dòng chứa prefix file và dòng subsection header label
    new_lines = []
    skip_label_line = False
    for line in lines:
        if prefix in line:
            continue  # xóa dòng file thuộc subsection
        if f"- {sub_label}:" in line:
            continue  # xóa dòng label subsection header
        new_lines.append(line)

    mkdocs_file.write_text("".join(new_lines), encoding="utf-8")


# ─── API: Rebuild MkDocs ─────────────────────────────────────────────────────

@app.route("/api/rebuild", methods=["POST"])
def rebuild():
    import shutil, os, sys
    # Mở rộng PATH để tìm mkdocs trong nhiều vị trí phổ biến
    extra_paths = [
        os.path.expanduser("~/.local/bin"),
        "/usr/local/bin",
        "/opt/conda/bin",
        "/opt/miniconda3/bin",
        os.path.dirname(sys.executable),
    ]
    env = os.environ.copy()
    env["PATH"] = ":".join(extra_paths) + ":" + env.get("PATH", "")

    mkdocs_bin = shutil.which("mkdocs", path=env["PATH"])
    if not mkdocs_bin:
        return jsonify({"ok": False, "error": "Không tìm thấy mkdocs. Hãy chạy: pip3 install mkdocs mkdocs-material"}), 500

    try:
        result = subprocess.run(
            [mkdocs_bin, "build", "--quiet"],
            cwd=str(REPO_DIR), capture_output=True, text=True, timeout=60, env=env
        )
        if result.returncode != 0:
            return jsonify({"ok": False, "error": result.stderr}), 500

        # Restart mkdocs serve để pick up mkdocs.yml mới
        subprocess.run(["pkill", "-f", "mkdocs serve"], capture_output=True)
        import time; time.sleep(0.8)
        subprocess.Popen(
            [mkdocs_bin, "serve", "-a", "0.0.0.0:8001"],
            cwd=str(REPO_DIR),
            env=env,
            stdout=open(REPO_DIR / "mkdocs.log", "w"),
            stderr=subprocess.STDOUT
        )

        return jsonify({"ok": True, "message": "Build & reload thành công!"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ─── API: Git push ───────────────────────────────────────────────────────────

@app.route("/api/git/push", methods=["POST"])
def git_push():
    data = request.json or {}
    message = data.get("message", "docs: cập nhật tài liệu qua admin editor")
    try:
        subprocess.run(["git", "add", "docs/", "mkdocs.yml"], cwd=str(REPO_DIR), check=True)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=str(REPO_DIR), capture_output=True, text=True
        )
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            return jsonify({"ok": False, "error": result.stderr}), 500
        push = subprocess.run(
            ["git", "push"],
            cwd=str(REPO_DIR), capture_output=True, text=True, timeout=30
        )
        if push.returncode != 0:
            return jsonify({"ok": False, "error": push.stderr}), 500
        return jsonify({"ok": True, "message": "Đã push lên GitHub!"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ─── Serve admin UI ──────────────────────────────────────────────────────────

@app.route("/")
@app.route("/<path:filename>")
def serve_ui(filename="index.html"):
    return send_from_directory("admin-ui", filename)

if __name__ == "__main__":
    print("🚀 Admin Editor  : http://10.0.7.169:5002")
    print("📖 Docs Site     : http://10.0.7.169:8001")
    app.run(host="0.0.0.0", port=5002, debug=False)
