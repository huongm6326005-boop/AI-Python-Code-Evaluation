import sqlite3

def get_user_by_username(username, db_path="database.db"):
    """
    Lấy thông tin người dùng từ bảng Users theo username.

    Args:
        username (str): Tên người dùng cần tìm.
        db_path (str): Đường dẫn tới file SQLite database.

    Returns:
        dict | None: Thông tin người dùng nếu tìm thấy, ngược lại trả về None.
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Trả về kết quả dạng dictionary
        cursor = conn.cursor()

        query = "SELECT * FROM Users WHERE username = ?"
        cursor.execute(query, (username,))

        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    except sqlite3.Error as e:
        print(f"Lỗi cơ sở dữ liệu: {e}")
        return None

    finally:
        if 'conn' in locals():
            conn.close()


# Ví dụ sử dụng
user = get_user_by_username("john_doe")

if user:
    print("Thông tin người dùng:")
    print(user)
else:
    print("Không tìm thấy người dùng.")
