import sqlite3
from typing import Optional

def get_user_by_username(username: str, db_path: str = "database.db") -> Optional[dict]:
    """
    Kết nối với SQLite và truy vấn thông tin người dùng theo username.
    
    Args:
        username: Tên người dùng cần tìm
        db_path: Đường dẫn tới file SQLite (mặc định: 'database.db')
    
    Returns:
        Dict chứa thông tin người dùng, hoặc None nếu không tìm thấy
    """
    try:
        # Kết nối database (tạo mới nếu chưa tồn tại)
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row  # Trả về kết quả dạng dict-like
            cursor = conn.cursor()

            # Dùng parameterized query để tránh SQL Injection
            cursor.execute(
                "SELECT * FROM Users WHERE username = ?",
                (username,)
            )

            row = cursor.fetchone()

            if row:
                return dict(row)  # Chuyển Row object thành dict
            return None

    except sqlite3.OperationalError as e:
        print(f"Lỗi cơ sở dữ liệu: {e}")
        return None
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
        return None


# ============================================================
# Demo: Tạo DB mẫu và kiểm thử hàm
# ============================================================
def _setup_demo_db(db_path: str):
    """Tạo bảng Users và dữ liệu mẫu để demo."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS Users")
        conn.execute("""
            CREATE TABLE Users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    NOT NULL UNIQUE,
                email    TEXT    NOT NULL,
                age      INTEGER,
                role     TEXT    DEFAULT 'user'
            )
        """)
        conn.executemany(
            "INSERT INTO Users (username, email, age, role) VALUES (?, ?, ?, ?)",
            [
                ("alice",   "alice@example.com",   30, "admin"),
                ("bob",     "bob@example.com",     25, "user"),
                ("charlie", "charlie@example.com", 35, "user"),
            ],
        )


if __name__ == "__main__":
    DB_PATH = "/tmp/demo.db"
    _setup_demo_db(DB_PATH)

    for name in ["alice", "bob", "unknown_user"]:
        print(f"\n🔍 Tìm username='{name}':")
        user = get_user_by_username(name, db_path=DB_PATH)
        if user:
            for key, value in user.items():
                print(f"   {key}: {value}")
        else:
            print("   ❌ Không tìm thấy người dùng.")
