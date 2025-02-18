import csv
import os
import numpy as np
from utils import calculate_median_rcs

csv_path = os.path.join("output","results", "sample_stock.csv")
data = []
with open(csv_path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)  # skip header if present
    for row in reader:
        data.append(row)

median = calculate_median_rcs(np.array(data, dtype=float))
print("Median", median)
print("CSV data:", data)