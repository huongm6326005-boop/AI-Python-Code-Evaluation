"""
Đọc file CSV dung lượng lớn (~10GB) và tính tổng cột 'Doanh_thu'.
Cung cấp 4 phương pháp với độ phức tạp tăng dần.
"""

import csv
import time
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# PHƯƠNG PHÁP Chunked Pandas (khuyên dùng)
# Đơn giản, nhanh, dễ mở rộng thêm xử lý logic
# ──────────────────────────────────────────────
def tinh_tong_doanh_thu_pandas(
    duong_dan: str,
    ten_cot: str = "Doanh_thu",
    chunk_size: int = 500_000,
) -> float:
    """
    Đọc CSV theo từng chunk bằng pandas và cộng dồn tổng.

    Args:
        duong_dan:  Đường dẫn tới file CSV.
        ten_cot:    Tên cột cần tính tổng (mặc định: 'Doanh_thu').
        chunk_size: Số dòng mỗi chunk (mặc định 500 000 dòng ≈ ~50–100 MB RAM).

    Returns:
        Tổng giá trị kiểu float.

    Raises:
        FileNotFoundError: Nếu file không tồn tại.
        KeyError:          Nếu cột không tìm thấy trong file.
    """
    duong_dan = Path(duong_dan)
    if not duong_dan.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {duong_dan}")

    tong = 0.0
    so_dong = 0
    so_dong_loi = 0
    bat_dau = time.perf_counter()

    logger.info("Bắt đầu đọc file: %s (chunk_size=%d)", duong_dan, chunk_size)

    with pd.read_csv(
        duong_dan,
        usecols=[ten_cot],          # Chỉ đọc cột cần thiết → tiết kiệm bộ nhớ
        chunksize=chunk_size,
        dtype={ten_cot: "float64"}, # Ép kiểu sớm để tránh object column
        on_bad_lines="warn",        # Bỏ qua dòng lỗi, không crash
        engine="c",                 # C engine nhanh hơn Python engine
    ) as reader:
        for chunk_so, chunk in enumerate(reader, start=1):
            so_dong_loi_chunk = chunk[ten_cot].isna().sum()
            so_dong_loi += so_dong_loi_chunk

            tong += chunk[ten_cot].sum(skipna=True)
            so_dong += len(chunk)

            if chunk_so % 10 == 0:
                logger.info(
                    "  Đã xử lý %d chunk (%d dòng), tổng tạm = %,.2f",
                    chunk_so, so_dong, tong,
                )

    thoi_gian = time.perf_counter() - bat_dau
    logger.info(
        "Hoàn tất | Tổng dòng: %d | Dòng lỗi/NA: %d | Thời gian: %.2fs | Tổng: %,.2f",
        so_dong, so_dong_loi, thoi_gian, tong,
    )
    return tong
