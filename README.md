# img2ascii

Converts images to ASCII art using a character ramp based on pixel brightness.

Combine multiple image processing algorithms for better results:
  - Block averaging
  - Contrast shaping
  - Bayer matrix dithering
  - Error-diffusion dithering (Floyd-Steinberg, JJN, Stucki)

## Installation

### Prerequisites

- Python3
- pip 

### Setup

1. Clone this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Convert an image to ASCII art and display in console:
```bash
python img2ascii.py image.png
```

### Options

```bash
python img2ascii.py [OPTIONS] IMAGE_FILE
```

**Options:**
- `-o, --output FILE`: Save ASCII art to file instead of printing to console
- `-s, --size WIDTHxHEIGHT`: Resize image before conversion (default: 80x40, max: 200x200)
- `--block-avg SIZE`: Apply block averaging with block size (default: 2)
- `--contrast STRENGTH`: Apply contrast shaping with strength factor (default: 1.5)
- `--dither-bayer SIZE`: Apply Bayer dithering with matrix size (2, 4, or 8)
- `--dither-error ALGORITHM`: Apply error-diffusion dithering (`floyd-steinberg`, `jjn`, `stucki`)
- `--clahe-clip-limit FLOAT`: Apply CLAHE with clip limit (default: 2.0, higher = more contrast)
- `--clahe-tile-size INT`: CLAHE tile size (default: 8, smaller = more local adaptation)
- `--use-space`: Use space character for darkest pixels instead of backtick
- `--maintain-aspect`: Maintain original aspect ratio while maximizing size within limits
- `-h, --help`: Show help message

### Examples

```bash
# Basic conversion
python img2ascii.py photo.jpg

# Save to file
python img2ascii.py photo.jpg -o ascii_art.txt

# Resize image before conversion
python img2ascii.py photo.jpg -s 100x50

# Apply block averaging for smoother output
python img2ascii.py photo.jpg --block-avg 3

# Enhance contrast for better detail visibility
python img2ascii.py photo.jpg --contrast 2.0

# Apply Bayer dithering for halftone effect
python img2ascii.py photo.jpg --dither-bayer 4

# Apply Floyd-Steinberg error diffusion
python img2ascii.py photo.jpg --dither-error floyd-steinberg

# Apply CLAHE for adaptive contrast enhancement
python img2ascii.py photo.jpg --clahe-clip-limit 3.0 --clahe-tile-size 6

# Use space for darkest pixels
python img2ascii.py photo.jpg --use-space

# Maintain aspect ratio while maximizing size
python img2ascii.py photo.jpg -s 100x50 --maintain-aspect

# Combine multiple algorithms
python img2ascii.py photo.jpg --block-avg 2 --contrast 1.5 --dither-error jjn

# Combine with CLAHE and other options
python img2ascii.py photo.jpg --block-avg 2 --clahe-clip-limit 2.5 --contrast 1.5 --dither-error jjn --use-space --maintain-aspect

# Combine with other options
python img2ascii.py photo.jpg -s 120x60 -o output.txt --block-avg 2 --contrast 1.8 --use-space --maintain-aspect
```

## Image Processing Algorithms

The converter includes several optional algorithms that can be combined to improve ASCII art quality:

### Block Averaging (`--block-avg`)
- **Purpose**: Reduces noise and creates smoother output
- **How it works**: Divides the image into blocks and averages pixel values within each block
- **Best for**: Noisy images, photos with fine details
- **Parameters**: Block size (2-8, default: 2)

### Contrast Shaping (`--contrast`)
- **Purpose**: Enhances contrast to make dark/light areas more distinct
- **How it works**: Applies contrast stretching to improve detail visibility
- **Best for**: Low-contrast images, photos with poor lighting
- **Parameters**: Strength factor (0.5-3.0, default: 1.5)

### Bayer Dithering (`--dither-bayer`)
- **Purpose**: Creates halftone effects using ordered dithering
- **How it works**: Uses Bayer matrices to create patterned threshold-based dithering
- **Best for**: Creating artistic halftone effects
- **Parameters**: Matrix size (2, 4, or 8)

### Error-Diffusion Dithering (`--dither-error`)
- **Purpose**: Creates smooth gradients using error diffusion
- **How it works**: Distributes quantization error to neighboring pixels
- **Best for**: Images with smooth gradients, portraits
- **Parameters**: Algorithm type:
  - `floyd-steinberg`: Fast, good for most images
  - `jjn`: Higher quality, slower processing
  - `stucki`: Balanced quality and speed

### CLAHE (`--clahe-clip-limit`, `--clahe-tile-size`)
- **Purpose**: Adaptive contrast enhancement that works locally on image regions
- **How it works**: Applies histogram equalization to small tiles while limiting contrast amplification
- **Best for**: Images with varying lighting conditions, medical images, low-contrast photos
- **Parameters**: 
  - Clip limit (0.1-10.0, default: 2.0): Higher values allow more contrast enhancement
  - Tile size (4-16, default: 8): Smaller tiles provide more local adaptation

### Algorithm Combinations
Algorithms are applied in optimal order: block averaging → CLAHE → contrast shaping → dithering → resize → ASCII conversion. You can combine multiple algorithms for best results.

## Development

### Algorithm Comparison

To compare different algorithms and see which works best for your images, run the algorithm comparison script:
```bash
python algorithm_comparison.py <image_path>
```

Example:
```bash
python algorithm_comparison.py photo.jpg
```

This script demonstrates all available algorithms with the same image, making it easy to see the differences and choose the best approach for your specific use case.

### Running Tests

Run the test suite:
```bash
python run_tests.py
```

## License

MIT
