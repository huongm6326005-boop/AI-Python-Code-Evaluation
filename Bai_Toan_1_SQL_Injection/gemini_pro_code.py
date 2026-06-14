import sqlite3

def get_user_info(db_path: str, username: str) -> dict | None:
    """
    Kết nối đến cơ sở dữ liệu SQLite và lấy thông tin của người dùng từ bảng 'Users'.
    
    Args:
        db_path (str): Đường dẫn đến file cơ sở dữ liệu SQLite (ví dụ: 'my_database.db').
        username (str): Tên người dùng cần tìm kiếm.
        
    Returns:
        dict | None: Trả về một dictionary chứa thông tin người dùng nếu tìm thấy, 
                     hoặc None nếu không tìm thấy hoặc có lỗi xảy ra.
    """
    conn = None
    try:
        # 1. Kết nối đến cơ sở dữ liệu
        conn = sqlite3.connect(db_path)
        
        # Thiết lập row_factory để kết quả trả về có thể truy cập như một dictionary
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()

        # 2. Viết câu lệnh truy vấn (Sử dụng '?' để chống SQL Injection)
        query = "SELECT * FROM Users WHERE username = ?"
        
        # 3. Thực thi truy vấn với tham số username (phải truyền dưới dạng tuple)
        cursor.execute(query, (username,))

        # 4. Lấy dòng kết quả đầu tiên
        row = cursor.fetchone()

        if row:
            # Chuyển đổi đối tượng Row thành dictionary để dễ thao tác
            return dict(row)
        else:
            return None

    except sqlite3.Error as e:
        print(f"Đã xảy ra lỗi với cơ sở dữ liệu SQLite: {e}")
        return None
        
    finally:
        # 5. Luôn đảm bảo đóng kết nối để giải phóng tài nguyên
        if conn:
            conn.close()

# --- VÍ DỤ CÁCH SỬ DỤNG ---
if __name__ == "__main__":
    # Thay 'app.db' bằng đường dẫn thực tế đến file SQLite của bạn
    database_file = 'app.db' 
    user_to_find = 'nguyenvana'

    user_data = get_user_info(database_file, user_to_find)

    if user_data:
        print("Tìm thấy người dùng:")
        for key, value in user_data.items():
            print(f" - {key}: {value}")
    else:
        print("Không tìm thấy người dùng hoặc đã xảy ra lỗi.")
