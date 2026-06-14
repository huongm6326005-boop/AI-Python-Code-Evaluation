import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Cấu hình thư mục lưu trữ và các định dạng file được phép
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Giới hạn dung lượng file upload (ví dụ: tối đa 16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Đảm bảo thư mục 'uploads' tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Hàm kiểm tra đuôi file có hợp lệ không"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload-avatar', methods=['POST'])
def upload_avatar():
    # 1. Kiểm tra xem request có chứa phần file không
    if 'avatar' not in request.files:
        return jsonify({'error': 'Không tìm thấy key "avatar" trong request'}), 400
    
    file = request.files['avatar']
    
    # 2. Nếu người dùng không chọn file mà bấm gửi
    if file.filename == '':
        return jsonify({'error': 'Chưa có file nào được chọn'}), 400
    
    # 3. Kiểm tra file hợp lệ và tiến hành lưu
    if file and allowed_file(file.filename):
        # Làm sạch tên file (ví dụ: "ảnh đại diện.jpg" -> "anh_dai_dien.jpg")
        filename = secure_filename(file.filename)
        
        # Tạo đường dẫn đầy đủ để lưu file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Lưu file vào thư mục server
        file.save(file_path)
        
        return jsonify({
            'message': 'Tải lên ảnh đại diện thành công!',
            'filename': filename,
            'path': f"/uploads/{filename}"
        }), 200
    
    else:
        return jsonify({'error': 'Định dạng file không hợp lệ. Chỉ chấp nhận png, jpg, jpeg, gif'}), 400

# Xử lý lỗi khi file quá dung lượng cho phép
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'Kích thước file quá lớn (Tối đa 16MB)'}), 413

if __name__ == '__main__':
    app.run(debug=True)
