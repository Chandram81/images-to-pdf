# Images to PDF

A lightweight Python GUI application for converting multiple images into a single PDF.

Built with **Tkinter** and **Pillow**, with optional **HEIC/HEIF** support using `pillow-heif`.

## Features

- Add multiple images at once
- Convert images into a single PDF
- Supports:
  - JPG / JPEG
  - PNG
  - WebP
  - BMP
  - TIFF
  - HEIC / HEIF
- Reorder images before conversion
- Move images up/down to control PDF page order
- Remove selected images
- Clear the complete image list
- Preserves image orientation using EXIF metadata
- Handles transparent PNG images with a white PDF background
- Choose the output PDF filename and location
- Automatically opens the output folder after successful conversion
- Simple Windows-friendly GUI
- No internet connection required during conversion

## Screenshots

_Add screenshots of the application here._

## Requirements

- Python 3.9+
- Pillow
- pillow-heif

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/images-to-pdf.git
cd images-to-pdf
