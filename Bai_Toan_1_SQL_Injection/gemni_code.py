import sqlite3


def get_user_by_username(db_name, username):
    """Kết nối tới SQLite và lấy thông tin người dùng theo username.

    Args:
        db_name (str): Tên tệp cơ sở dữ liệu (ví dụ: 'my_database.db').
        username (str): Tên người dùng cần tìm kiếm.

    Returns:
        dict/None: Trả về một dictionary chứa thông tin người dùng nếu tìm thấy,
                   hoặc None nếu không tìm thấy hoặc có lỗi xảy ra.
    """
    conn = None
    try:
        # 1. Thiết lập kết nối đến cơ sở dữ liệu
        conn = sqlite3.connect(db_name)

        # Cấu hình này giúp kết quả trả về ở dạng có thể truy cập bằng tên cột (giống dict)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 2. Viết câu lệnh SQL với tham số ẩn (?) để chống SQL Injection
        query = "SELECT * FROM Users WHERE username = ?"

        # 3. Thực thi câu lệnh (tham số truyền vào phải là một tuple: (username,))
        cursor.execute(query, (username,))

        # 4. Lấy ra một bản ghi đầu tiên tìm được
        row = cursor.fetchone()

        if row:
            # Chuyển đổi sqlite3.Row thành một dictionary thông thường để dễ sử dụng
            return dict(row)
        else:
            print(f"Không tìm thấy người dùng có username: {username}")
            return None

    except sqlite3.Error as e:
        print(f"Đã xảy ra lỗi khi kết nối hoặc truy vấn SQLite: {e}")
        return None

    finally:
        # 5. Đảm bảo đóng kết nối luôn được thực hiện, ngay cả khi có lỗi
        if conn:
            conn.close()
