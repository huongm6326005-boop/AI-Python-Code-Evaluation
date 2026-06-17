import sqlite3

# Kết nối (và tự động tạo) file database.db
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# 1. Tạo bảng Users
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT,
        age INTEGER
    )
''')

# 2. Xóa dữ liệu cũ (nếu bạn lỡ chạy file này nhiều lần) để tránh lỗi trùng lặp
cursor.execute("DELETE FROM Users WHERE username = 'john_doe'")

# 3. Thêm dữ liệu giả (Dummy data) để test
cursor.execute('''
    INSERT INTO Users (username, email, age) 
    VALUES ('john_doe', 'john.doe@example.com', 28)
''')

# Lưu thay đổi và đóng kết nối
conn.commit()
conn.close()

print("✅ Đã chuẩn bị xong file database.db và thêm user 'john_doe'!")