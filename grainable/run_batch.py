#!/usr/bin/env python3
"""
Batch runner for Grainable ice‑core images.

Usage
-----
$ python run_batch.py               # processes everything in bag‑list.txt
$ python run_batch.py NEEM_3661     # process a single sample ID
"""
from pathlib import Path
import sys
import pandas as pd
from utils.image_processing import (
    load_full_image, crop_image,
    denoise, threshold, hessian_filter, cleaning,
    label_grains,                           # <- unchanged import
)

project_root  = Path(__file__).resolve().parents[1]
data_dir      = project_root / "data"
raw_img_dir   = data_dir / "raw-images"
bag_list_file = data_dir / "bag-list.txt"

samples = [sys.argv[1]] if len(sys.argv) > 1 else \
          [s.strip() for s in bag_list_file.read_text().splitlines() if s.strip()]

LEN_CROP, OVERLAP = 4000, 200
slicing_df = pd.read_csv(data_dir / "csv" / "slicing_param.csv")

for sid in samples:
    img_path = raw_img_dir / f"{sid}.png"
    if not img_path.exists():
        print(f"[WARN] {img_path} not found – skipping"); continue

    img, _ = load_full_image(img_path.name, raw_img_dir, LEN_CROP, OVERLAP, slicing_df)

    for idx, crop in enumerate(crop_image(img, LEN_CROP, OVERLAP)):
        mask = cleaning(hessian_filter(threshold(denoise(crop))))
        # --> Generate CSV only (no preview PNGs)
        label_grains(mask, crop, sid + ".png", idx, pixels_to_um=5.0, save_images=False)

print("✅ batch run complete (CSV‑only)")