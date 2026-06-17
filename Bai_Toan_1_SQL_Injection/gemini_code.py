import sqlite3

# ==========================================
# 1. HÀM KHỞI TẠO DATABASE VÀ DỮ LIỆU MẪU
# ==========================================
def init_database(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Tạo bảng Users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Thêm dữ liệu mẫu
        sample_users = [
            ('hoang_nam', 'Nguyễn Hoàng Nam', 'nam@example.com'),
            ('thu_ha', 'Trần Thị Thu Hà', 'ha.tran@example.com'),
            ('john_doe', 'John Doe', 'john@example.com')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO Users (username, full_name, email)
            VALUES (?, ?, ?)
        ''', sample_users)

        conn.commit()
        print(f"🎉 Đã khởi tạo thành công file '{db_name}' và thêm dữ liệu mẫu!")

    except sqlite3.Error as e:
        print(f"Có lỗi khi khởi tạo database: {e}")
    finally:
        if conn:
            conn.close()


# ==========================================
# 2. HÀM TÌM KIẾM NGƯỜI DÙNG BẰNG USERNAME
# ==========================================
def get_user_by_username(db_name, username):
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        conn.row_factory = sqlite3.Row  # Giúp trả về kết quả dạng giống dict
        cursor = conn.cursor()

        query = "SELECT * FROM Users WHERE username = ?"
        cursor.execute(query, (username,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        else:
            print(f"❌ Không tìm thấy người dùng có username: '{username}'")
            return None

    except sqlite3.Error as e:
        print(f"Đã xảy ra lỗi khi truy vấn: {e}")
        return None
    finally:
        if conn:
            conn.close()


# ==========================================
# 3. CHƯƠNG TRÌNH CHÍNH (CHẠY THỬ)
# ==========================================
if __name__ == "__main__":
    db_file = "company.db"

    # Bước A: Chạy hàm tạo file .db và nạp dữ liệu
    init_database(db_file)

    print("-" * 40)

    # Bước B: Chạy thử hàm tìm kiếm user thành công
    print("🔎 Đang tìm kiếm user 'hoang_nam'...")
    user1 = get_user_by_username(db_file, "hoang_nam")
    if user1:
        print("Kết quả trả về:")
        print(user1)

    print("-" * 40)

    # Bước C: Chạy thử trường hợp tìm user không tồn tại
    print("🔎 Đang tìm kiếm user 'ong_ba_beo'...")
    user2 = get_user_by_username(db_file, "ong_ba_beo")