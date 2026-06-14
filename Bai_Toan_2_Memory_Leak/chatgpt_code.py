import pandas as pd

def tong_doanh_thu(file_path, chunk_size=100_000):
    tong = 0.0

    for chunk in pd.read_csv(
        file_path,
        usecols=["Doanh_thu"],
        chunksize=chunk_size
    ):
        tong += chunk["Doanh_thu"].sum()

    return tong


# Ví dụ sử dụng
if __name__ == "__main__":
    file_csv = "du_lieu_lon.csv"
    ket_qua = tong_doanh_thu(file_csv)
    print(f"Tổng doanh thu: {ket_qua}")
