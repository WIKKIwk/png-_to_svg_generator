# PNG to SVG Generator

A high-quality PNG to SVG converter that preserves image quality during the conversion process.

## Features

- 🖼️ Converts PNG images to SVG format
- 🎯 Preserves image quality and details
- 🔄 Batch conversion support
- 📁 Automatic output directory management
- 🖥️ Beautiful web-based UI for easy conversion

## Project Structure

```
├── image.png              # Source PNG image 1
├── image copy.png         # Source PNG image 2
├── convert.py             # Python conversion script
├── index.html             # Web-based converter UI
├── requirements.txt       # Python dependencies
├── output/                # Generated SVG files
└── README.md              # This file
```

## Quick Start

### Using Python Script

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the converter:
   ```bash
   python3 convert.py
   ```

3. Find your SVG files in the `output/` directory.

### Using Web UI

1. Open `index.html` in your browser
2. Drag & drop PNG files or click to select
3. Download converted SVG files

## How It Works

The converter uses **image tracing** technology to convert raster PNG images into scalable vector SVG format:

1. **Preprocessing**: The image is loaded and converted to grayscale
2. **Thresholding**: Adaptive thresholding is applied to create a clean binary image
3. **Tracing**: The bitmap is traced to generate vector paths
4. **Output**: Clean SVG markup is generated with optimized paths

## Requirements

- Python 3.8+
- Pillow (PIL)
- NumPy

## License

MIT License
