# Grainable-ice

Grainable-ice provides Python scripts and notebooks for processing and analyzing high-resolution xLASM images of ice cores to measure grain size properties.

## Features

* Processes high-resolution ice core line scan images (.png).
* Segments large images into smaller, overlapping sections based on configuration.
* Applies image processing techniques:
* Denoising
* Binarization and cleaning using bubble masks and morphological operations.
* Hessian filtering for finding grain boundaries
* Labels individual grains within processed image segments.
* Calculates grain properties (e.g., size) using a defined pixel-to-micrometer conversion factor.
* Saves processed outputs:
* Labeled image segments (PNG).
* Raw cropped image segments (PNG).
* Grain properties data (CSV).

## Project Structure

```
Grainable-ice/
├── .gitignore
├── LICENSE
├── README.md
├── data/                 # Input data
│   ├── bag-list.txt      # List of image filenames to process
│   ├── slicing_param.csv # Slicing parameters for images
│   ├── csv/              # grain data in bag per file
│   └── raw-images/       # Directory for input high-resolution PNG images
├── grainable/            # Core scripts (e.g., run_batch.py)
├── notebooks/            # Jupyter notebooks for processing and analysis
│   ├── 01_slice-dataframe.ipynb   # removes background
│   ├── 02_GS-properties-V2.ipynb  # image processing for single image files. Generates csv
│   ├── 03_Grain_size_depth.ipynb  # Loads NEEM csv bag files and plots over depth
│   ├── 04_Grain_shapes.ipynb  # Plots grain shapes against other parameters
│   └── output/           # Default output directory for results
│       ├── Plots/        # Output for labeled and raw image segments
│       └── Data_csv/     # Output for grain properties CSV files
├── tests/                # Notebooks for testing and specific analyses
└── utils/                # Utility Python modules (funtcitons, plotting,...)
```

## Setup

1.  **Setup:**
    *   Place your high-resolution ice core line scan images (PNG format) into the `data/raw-images/` directory.
    *   Edit `data/bag-list.txt` to list the base filenames (without `.png`) of the images you want to process, one per line.
    *   Ensure `data/csv/slicing_param.csv` contains the necessary slicing parameters for your images.
    *   Configure processing parameters (e.g., `pixels_to_um`, `crop_img_len_cm`, `overlap_cm`) within the notebook cells under "1. Setup Paths and Parameters".
2.  **Output:** Main result consist of csv files per bag with the regionpprops properties

## Installation

To use Grainable-ice, clone the repository and install the necessary dependencies.

```bash
git clone https://github.com/yourusername/Grainable-ice.git # Replace with your actual repo URL
cd Grainable-ice
# It's recommended to create a virtual environment first
# python -m venv venv

```