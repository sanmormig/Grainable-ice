"""
Image processing utilities for the Grainable‑ice project.

"""
from __future__ import annotations

# ‑‑‑ stdlib ‑‑‑
import logging
import os
from os.path import join
from pathlib import Path

# ‑‑‑ third‑party ‑‑‑
import numpy as np
import pandas as pd
from PIL import Image
from scipy.ndimage import generate_binary_structure, label as nd_label

# ‑‑‑ scikit‑image ‑‑‑
from skimage import (
    color,
    exposure,
    filters,
    img_as_float,
    img_as_ubyte,
    io,
    measure,
    morphology,
)
from skimage.segmentation import clear_border

Image.MAX_IMAGE_PIXELS = 2_000_000_000  # allow very large scans

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # Grainable‑ice/

__all__ = [
    "load_full_image",
    "crop_image",
    "denoise",
    "threshold",
    "hessian_filter",
    "cleaning",
    "label_grains",
]

# ───────────────── helpers ──────────────────

def load_full_image(file_name: str, file_path: str | Path, len_crop_img_px: int, overlap_px: int, df_slicing: pd.DataFrame):
    df_slic_img = df_slicing[df_slicing["name"] == file_name[:-4]]
    img_path = join(file_path, file_name)
    img = io.imread(img_path)
    total_length = df_slic_img["px_right"].iloc[0] - df_slic_img["px_left"].iloc[0]
    n = int((total_length - overlap_px) / (len_crop_img_px - overlap_px))
    logging.info("Loaded %s • shape=%s • slices=%d", file_name, img.shape, n)
    return img, n


def crop_image(img: np.ndarray, len_crop_img_px: int, overlap_px: int):
    h = img.shape[0]
    step = len_crop_img_px - overlap_px
    for start in range(0, h - len_crop_img_px + 1, step):
        end = start + len_crop_img_px
        yield img[start:end]


def denoise(img: np.ndarray) -> np.ndarray:
    from skimage.restoration import denoise_bilateral

    img_float = img_as_float(img)
    img_denoised = denoise_bilateral(img_float, sigma_color=0.05, sigma_spatial=15)
    return exposure.equalize_adapthist(img_denoised, clip_limit=0.03)


def threshold(img: np.ndarray) -> np.ndarray:
    thresh_val = filters.threshold_otsu(img)
    return img > thresh_val


def hessian_filter(img: np.ndarray) -> np.ndarray:
    from skimage.filters import frangi

    return frangi(img, scale_range=(1, 3), beta1=0.5, beta2=15)


def cleaning(binary: np.ndarray, min_size: int = 500) -> np.ndarray:
    cleaned = morphology.remove_small_objects(binary, min_size=min_size)
    return clear_border(cleaned)

# ───────────────── label_grains ──────────────────

def label_grains(
    clean_img: np.ndarray,
    original_img: np.ndarray,
    file_name: str,
    n: int,
    pixels_to_um: float | None = None,
    save_images: bool = True,
    return_preview: bool = False,
):
    clean_img: np.ndarray,
    original_img: np.ndarray,
    file_name: str,
    n: int,
    pixels_to_um: float | None = None,
    save_images: bool = True,
):
    """Legacy grain labelling routine with optional image saving.

    Parameters
    ----------
    clean_img
        Boolean mask (1 = grain).
    original_img
        Greyscale/RGB crop.
    file_name
        Name of the source image (used for directories).
    n
        Slice index appended to outputs.
    pixels_to_um
        µm per pixel (if you later want area‑µm² outside).
    save_images
        If *False*, skip writing preview + raw PNGs (good for batch mode).
    """
    mask = clean_img == 1
    cleared_img = clear_border(mask)
    s = generate_binary_structure(2, 1)
    labeled_mask, num_labels = nd_label(cleared_img, structure=s)

    if save_images:
        label_color = color.label2rgb(labeled_mask)
        uint = img_as_ubyte(label_color)
        out_img_dir = PROJECT_ROOT / "notebooks" / "Plots" / "NEEM_Labeled_and_Raw_Images" / file_name[:-4]
        out_img_dir.mkdir(parents=True, exist_ok=True)
        io.imsave(out_img_dir / f"{file_name[:-4]}_{n}.png", uint)
        io.imsave(out_img_dir / f"{file_name[:-4]}_{n}_raw.png", original_img)
        logging.info("images saved • %d grains", num_labels)

    clusters = measure.regionprops(labeled_mask, original_img)

    propList = [
        "area",
        "equivalent_diameter",
        "centroid_x",
        "centroid_y",
        "orientation",
        "major_axis_length",
        "minor_axis_length",
        "perimeter",
    ]

    csv_dir = PROJECT_ROOT / "data" / "csv" / "grain_properties" / file_name[:-4]
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_path = csv_dir / file_name.replace(".png", f"_{n}.csv")

    with open(csv_path, "w") as fh:
        fh.write("," + ",".join(propList) + "\n")
        for cluster in clusters:
            fh.write(str(cluster.label))
            for prop in propList:
                if prop == "area":
                    to_print = cluster.area
                elif prop == "orientation":
                    to_print = cluster.orientation * 57.2958
                elif prop == "centroid_x":
                    to_print = cluster.centroid[1]
                elif prop == "centroid_y":
                    to_print = cluster.centroid[0]
                else:
                    to_print = getattr(cluster, prop)
                fh.write("," + str(to_print))
            fh.write("\n")
    logging.info("CSV written • %s", csv_path)

    if return_preview:
        return img_as_ubyte(color.label2rgb(labeled_mask))
    return None
 • %s", csv_path)
