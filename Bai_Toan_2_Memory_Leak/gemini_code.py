import pandas as pd


def tinh_tong_doanh_thu_pandas(file_path, chunk_size=100000):
    tong_doanh_thu = 0

    # Sử dụng chunksize để đọc file theo từng phần nhỏ
    for chunk in pd.read_csv(
        file_path, chunksize=chunk_size, usecols=["Doanh_thu"]
    ):
        # usecols=['Doanh_thu'] giúp tối ưu tốc độ bằng cách chỉ tối giản bộ nhớ cho cột này
        tong_doanh_thu += chunk["Doanh_thu"].sum()

    return tong_doanh_thu


# Cách sử dụng:
# file_lon = 'du_lieu_khong_lo.csv'
# tong = tinh_tong_doanh_thu_pandas(file_lon)
# print(f"Tổng doanh thu là: {tong}")
