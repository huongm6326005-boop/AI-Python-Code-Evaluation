import os
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Thư mục lưu avatar
UPLOAD_FOLDER = "uploads/avatars"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Các định dạng ảnh cho phép
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/api/upload-avatar", methods=["POST"])
def upload_avatar():
    # Kiểm tra có file trong request hay không
    if "avatar" not in request.files:
        return jsonify({
            "success": False,
            "message": "Không tìm thấy file avatar"
        }), 400

    file = request.files["avatar"]

    # Kiểm tra người dùng có chọn file hay không
    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "Chưa chọn file"
        }), 400

    # Kiểm tra định dạng file
    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": "Định dạng file không được hỗ trợ"
        }), 400

    # Tạo tên file mới tránh trùng lặp
    extension = file.filename.rsplit(".", 1)[1].lower()
    new_filename = f"{uuid.uuid4().hex}.{extension}"

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(new_filename)
    )

    # Lưu file
    file.save(file_path)

    return jsonify({
        "success": True,
        "message": "Upload avatar thành công",
        "filename": new_filename,
        "path": file_path
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
