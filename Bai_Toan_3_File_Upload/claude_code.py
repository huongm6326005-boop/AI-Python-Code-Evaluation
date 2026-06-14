import os
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ─── Cấu hình ────────────────────────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads", "avatars")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ─── Helper ──────────────────────────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    """Kiểm tra phần mở rộng file có hợp lệ không."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def unique_filename(original: str) -> str:
    """Tạo tên file duy nhất: <uuid>.<ext> để tránh ghi đè."""
    ext = original.rsplit(".", 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"


# ─── Endpoint: Upload Avatar ──────────────────────────────────────────────────
@app.route("/api/avatar/upload", methods=["POST"])
def upload_avatar():
    """
    Upload ảnh đại diện.

    Request  : multipart/form-data
               field  : avatar  (file)
               field  : user_id (string, tuỳ chọn – để tổ chức thư mục riêng)

    Response : 201 Created  – { success, message, filename, url, size_bytes }
               400 Bad Request – khi thiếu file hoặc định dạng sai
               413 Payload Too Large – khi file vượt giới hạn 5 MB
    """

    # 1. Kiểm tra có file trong request chưa
    if "avatar" not in request.files:
        return jsonify({"success": False, "message": "Không tìm thấy file. Hãy gửi field 'avatar'."}), 400

    file = request.files["avatar"]

    # 2. Kiểm tra người dùng có chọn file chưa
    if file.filename == "":
        return jsonify({"success": False, "message": "Chưa chọn file."}), 400

    # 3. Kiểm tra định dạng
    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": f"Định dạng không được hỗ trợ. Chỉ chấp nhận: {', '.join(ALLOWED_EXTENSIONS)}.",
        }), 400

    # 4. Lưu file
    safe_original = secure_filename(file.filename)   # bảo vệ khỏi path traversal
    new_filename  = unique_filename(safe_original)    # tên duy nhất, không ghi đè

    # Tuỳ chọn: tạo thư mục con theo user_id
    user_id = request.form.get("user_id", "").strip()
    save_dir = os.path.join(app.config["UPLOAD_FOLDER"], user_id) if user_id else app.config["UPLOAD_FOLDER"]
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, new_filename)
    file.save(save_path)

    file_size = os.path.getsize(save_path)

    # URL công khai (điều chỉnh base URL theo môi trường thực tế)
    public_url = f"/uploads/avatars/{user_id + '/' if user_id else ''}{new_filename}"

    return jsonify({
        "success"    : True,
        "message"    : "Tải ảnh đại diện thành công.",
        "filename"   : new_filename,
        "url"        : public_url,
        "size_bytes" : file_size,
    }), 201


# ─── Error handlers ───────────────────────────────────────────────────────────
@app.errorhandler(413)
def request_entity_too_large(_):
    return jsonify({
        "success": False,
        "message": f"File quá lớn. Kích thước tối đa là {MAX_CONTENT_LENGTH // (1024 * 1024)} MB.",
    }), 413


# ─── Chạy server ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
