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
# PHƯƠNG PHÁP 1: Chunked Pandas (khuyên dùng)
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


# ──────────────────────────────────────────────
# PHƯƠNG PHÁP 2: csv module thuần Python
# Không cần thư viện ngoài, RAM thấp nhất
# ──────────────────────────────────────────────
def tinh_tong_doanh_thu_csv(
    duong_dan: str,
    ten_cot: str = "Doanh_thu",
    encoding: str = "utf-8",
) -> float:
    """
    Dùng module csv tích hợp sẵn, đọc từng dòng (streaming).
    Phù hợp khi không cài được pandas.
    """
    duong_dan = Path(duong_dan)
    if not duong_dan.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {duong_dan}")

    tong = 0.0
    so_dong = 0
    so_dong_loi = 0

    with open(duong_dan, newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)

        if ten_cot not in (reader.fieldnames or []):
            raise KeyError(f"Cột '{ten_cot}' không tồn tại. Các cột: {reader.fieldnames}")

        for dong in reader:
            so_dong += 1
            gia_tri = dong.get(ten_cot, "").strip()
            try:
                tong += float(gia_tri)
            except (ValueError, TypeError):
                so_dong_loi += 1

            if so_dong % 1_000_000 == 0:
                logger.info("  Đã xử lý %d triệu dòng, tổng tạm = %,.2f", so_dong // 1_000_000, tong)

    logger.info("Tổng dòng: %d | Dòng lỗi: %d | Tổng: %,.2f", so_dong, so_dong_loi, tong)
    return tong


# ──────────────────────────────────────────────
# PHƯƠNG PHÁP 3: Đa luồng (ThreadPoolExecutor)
# Tăng tốc trên file đặt trên SSD/NVMe
# ──────────────────────────────────────────────
from concurrent.futures import ThreadPoolExecutor, as_completed


def _xu_ly_chunk(args):
    """Hàm con xử lý một chunk, dùng cho đa luồng."""
    duong_dan, skiprows, nrows, ten_cot = args
    try:
        chunk = pd.read_csv(
            duong_dan,
            usecols=[ten_cot],
            skiprows=range(1, skiprows + 1),  # bỏ qua các dòng đã xử lý
            nrows=nrows,
            header=0 if skiprows == 0 else None,
            names=[ten_cot] if skiprows > 0 else None,
            dtype={ten_cot: "float64"},
            engine="c",
        )
        return chunk[ten_cot].sum(skipna=True)
    except Exception as exc:
        logger.warning("Lỗi chunk tại dòng %d: %s", skiprows, exc)
        return 0.0


def tinh_tong_doanh_thu_da_luong(
    duong_dan: str,
    ten_cot: str = "Doanh_thu",
    chunk_size: int = 1_000_000,
    so_luong: int = 4,
) -> float:
    """
    Chia file thành nhiều đoạn, xử lý song song bằng thread pool.

    Lưu ý: I/O bound → dùng thread (không phải process) là hợp lý.
    """
    # Đếm tổng số dòng trước (bỏ qua header)
    logger.info("Đang đếm tổng số dòng...")
    with open(duong_dan, "rb") as f:
        tong_dong = sum(1 for _ in f) - 1  # trừ header

    logger.info("Tổng số dòng dữ liệu: %d", tong_dong)

    cac_tham_so = [
        (duong_dan, i, min(chunk_size, tong_dong - i), ten_cot)
        for i in range(0, tong_dong, chunk_size)
    ]

    tong = 0.0
    with ThreadPoolExecutor(max_workers=so_luong) as executor:
        futures = {executor.submit(_xu_ly_chunk, p): p for p in cac_tham_so}
        for future in as_completed(futures):
            tong += future.result()

    logger.info("Tổng (đa luồng): %,.2f", tong)
    return tong


# ──────────────────────────────────────────────
# PHƯƠNG PHÁP 4: Dask — tự động song song hoá
# Tốt nhất cho cluster hoặc máy nhiều nhân
# ──────────────────────────────────────────────
def tinh_tong_doanh_thu_dask(
    duong_dan: str,
    ten_cot: str = "Doanh_thu",
) -> float:
    """
    Dùng Dask để tự động chia nhỏ và song song hoá.
    Cài đặt: pip install dask[dataframe]
    """
    try:
        import dask.dataframe as dd
    except ImportError:
        raise ImportError("Chạy: pip install dask[dataframe]")

    logger.info("Đang tính tổng bằng Dask...")
    ddf = dd.read_csv(duong_dan, usecols=[ten_cot], dtype={ten_cot: "float64"})
    tong = float(ddf[ten_cot].sum().compute())
    logger.info("Tổng (Dask): %,.2f", tong)
    return tong


# ──────────────────────────────────────────────
# Demo sử dụng
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Tính tổng cột Doanh_thu từ file CSV lớn")
    parser.add_argument("file", help="Đường dẫn file CSV")
    parser.add_argument("--cot", default="Doanh_thu", help="Tên cột (mặc định: Doanh_thu)")
    parser.add_argument(
        "--method",
        choices=["pandas", "csv", "thread", "dask"],
        default="pandas",
        help="Phương pháp đọc (mặc định: pandas)",
    )
    args = parser.parse_args()

    if args.method == "pandas":
        ket_qua = tinh_tong_doanh_thu_pandas(args.file, args.cot)
    elif args.method == "csv":
        ket_qua = tinh_tong_doanh_thu_csv(args.file, args.cot)
    elif args.method == "thread":
        ket_qua = tinh_tong_doanh_thu_da_luong(args.file, args.cot)
    else:
        ket_qua = tinh_tong_doanh_thu_dask(args.file, args.cot)

    print(f"\n✅ Tổng {args.cot}: {ket_qua:,.2f}")
