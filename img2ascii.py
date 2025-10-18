#!/usr/bin/env python3
"""
Image to ASCII Art Converter

A Python program that converts images to ASCII art using a character ramp
based on pixel brightness. Supports resizing images before conversion and
can output to console or save to a file.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Tuple, List
import numpy as np

try:
    from PIL import Image
except ImportError:
    print("Error: PIL (Pillow) is required. Install it with: pip install Pillow")
    sys.exit(1)


# Constants
ASCII_RAMP = "` .-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"
DEFAULT_SIZE = (80, 40)
MAX_WIDTH = 200
MAX_HEIGHT = 200


class ImageToAsciiConverter:
    """Converts images to ASCII art."""
    
    def __init__(self, ascii_ramp: str = ASCII_RAMP, use_space: bool = False):
        """
        Initialize the converter with an ASCII character ramp.
        
        Args:
            ascii_ramp: String of characters ordered from darkest to lightest
            use_space: If True, replace the first character with a space
        """
        if use_space and ascii_ramp:
            self.ascii_ramp = ' ' + ascii_ramp[1:]
        else:
            self.ascii_ramp = ascii_ramp
        self.ramp_length = len(self.ascii_ramp)
    
    def load_image(self, image_path: str) -> Image.Image:
        """Load an image from the given path."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            image = Image.open(path)
            return image
        except Exception as e:
            raise ValueError(f"Invalid image file: {e}")
    
    def resize_image(self, image: Image.Image, size: Tuple[int, int], maintain_aspect: bool = False) -> Image.Image:
        """Resize an image to the specified dimensions."""
        if maintain_aspect:
            # Calculate dimensions that maintain aspect ratio while maximizing size
            img_width, img_height = image.size
            
            # Calculate scaling factors maximizing the size within the limits
            width_scale = MAX_WIDTH / img_width
            height_scale = MAX_HEIGHT / img_height
            
            # Use the smaller scale to ensure both dimensions fit within limits
            scale = min(width_scale, height_scale)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            width, height = size
            return image.resize((width, height), Image.Resampling.LANCZOS)
    
    def image_to_grayscale(self, image: Image.Image) -> Image.Image:
        """Convert an image to grayscale."""
        if image.mode != 'L':
            return image.convert('L')
        return image
    
    def pixel_to_ascii(self, pixel_value: int) -> str:
        """Convert a pixel brightness value to an ASCII character."""
        index = int((pixel_value / 255.0) * (self.ramp_length - 1))
        return self.ascii_ramp[index]
    
    def apply_block_averaging(self, image: Image.Image, block_size: int = 2) -> Image.Image:
        """Apply block averaging to reduce noise and create smoother output."""
        img_array = np.array(image)
        height, width = img_array.shape
        
        new_height = height // block_size
        new_width = width // block_size
        
        result = np.zeros((new_height, new_width), dtype=np.uint8)
        
        for y in range(new_height):
            for x in range(new_width):
                # Extract block
                y_start = y * block_size
                y_end = min(y_start + block_size, height)
                x_start = x * block_size
                x_end = min(x_start + block_size, width)
                
                block = img_array[y_start:y_end, x_start:x_end]
                result[y, x] = int(np.mean(block))
        
        return Image.fromarray(result, mode='L')
    
    def apply_contrast_shaping(self, image: Image.Image, strength: float = 1.5) -> Image.Image:
        """Enhance contrast using simple contrast stretching."""
        img_array = np.array(image, dtype=np.float32)
        
        # Apply contrast stretching
        min_val = np.min(img_array)
        max_val = np.max(img_array)
        
        if max_val > min_val:
            # Normalize to 0-1
            normalized = (img_array - min_val) / (max_val - min_val)
            # Apply contrast enhancement
            enhanced = np.power(normalized, 1.0 / strength)
            # Scale back to 0-255
            result = enhanced * 255
        else:
            result = img_array
        
        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8), mode='L')
    
    def apply_bayer_dithering(self, image: Image.Image, matrix_size: int = 4) -> Image.Image:
        """Apply Bayer matrix dithering for halftone effect."""
        # Bayer matrices
        bayer_2x2 = np.array([[0, 2], [3, 1]], dtype=np.float32) / 4
        bayer_4x4 = np.array([
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
        ], dtype=np.float32) / 16
        bayer_8x8 = np.array([
            [0, 32, 8, 40, 2, 34, 10, 42],
            [48, 16, 56, 24, 50, 18, 58, 26],
            [12, 44, 4, 36, 14, 46, 6, 38],
            [60, 28, 52, 20, 62, 30, 54, 22],
            [3, 35, 11, 43, 1, 33, 9, 41],
            [51, 19, 59, 27, 49, 17, 57, 25],
            [15, 47, 7, 39, 13, 45, 5, 37],
            [63, 31, 55, 23, 61, 29, 53, 21]
        ], dtype=np.float32) / 64
        
        if matrix_size == 2:
            bayer_matrix = bayer_2x2
        elif matrix_size == 4:
            bayer_matrix = bayer_4x4
        elif matrix_size == 8:
            bayer_matrix = bayer_8x8
        else:
            raise ValueError("Matrix size must be 2, 4, or 8")
        
        img_array = np.array(image, dtype=np.float32)
        height, width = img_array.shape
        result = np.zeros_like(img_array)
        
        for y in range(height):
            for x in range(width):
                # Get threshold from Bayer matrix
                threshold = bayer_matrix[y % matrix_size, x % matrix_size] * 255
                # Apply dithering
                result[y, x] = 255 if img_array[y, x] > threshold else 0
        
        return Image.fromarray(result.astype(np.uint8), mode='L')
    
    def apply_error_diffusion(self, image: Image.Image, algorithm: str = 'floyd-steinberg') -> Image.Image:
        """Apply error-diffusion dithering using specified algorithm."""
        img_array = np.array(image, dtype=np.float32)
        height, width = img_array.shape
        result = np.zeros_like(img_array)
        error = np.zeros_like(img_array)
        
        # Define diffusion matrices
        if algorithm == 'floyd-steinberg':
            # Floyd-Steinberg matrix
            diffusion = [
                (0, 1, 7/16),
                (1, -1, 3/16),
                (1, 0, 5/16),
                (1, 1, 1/16)
            ]
        elif algorithm == 'jjn':
            # Jarvis-Judice-Ninke matrix
            diffusion = [
                (0, 1, 7/48), (0, 2, 5/48),
                (1, -2, 3/48), (1, -1, 5/48), (1, 0, 7/48), (1, 1, 5/48), (1, 2, 3/48),
                (2, -2, 1/48), (2, -1, 3/48), (2, 0, 5/48), (2, 1, 3/48), (2, 2, 1/48)
            ]
        elif algorithm == 'stucki':
            # Stucki matrix
            diffusion = [
                (0, 1, 8/42), (0, 2, 4/42),
                (1, -2, 2/42), (1, -1, 4/42), (1, 0, 8/42), (1, 1, 4/42), (1, 2, 2/42),
                (2, -2, 1/42), (2, -1, 2/42), (2, 0, 4/42), (2, 1, 2/42), (2, 2, 1/42)
            ]
        else:
            raise ValueError("Algorithm must be 'floyd-steinberg', 'jjn', or 'stucki'")
        
        for y in range(height):
            for x in range(width):
                # Quantize pixel
                old_pixel = img_array[y, x] + error[y, x]
                new_pixel = 255 if old_pixel > 127 else 0
                result[y, x] = new_pixel
                
                # Calculate error
                quant_error = old_pixel - new_pixel
                
                # Distribute error
                for dy, dx, weight in diffusion:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width:
                        error[ny, nx] += quant_error * weight
        
        return Image.fromarray(result.astype(np.uint8), mode='L')
    
    def apply_clahe(self, image: Image.Image, clip_limit: float = 2.0, tile_size: int = 8) -> Image.Image:
        """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
        img_array = np.array(image, dtype=np.float32)
        height, width = img_array.shape
        
        tiles_y = (height + tile_size - 1) // tile_size
        tiles_x = (width + tile_size - 1) // tile_size
        
        lookup_tables = np.zeros((tiles_y, tiles_x, 256), dtype=np.float32)
        
        for ty in range(tiles_y):
            for tx in range(tiles_x):
                y_start = ty * tile_size
                y_end = min(y_start + tile_size, height)
                x_start = tx * tile_size
                x_end = min(x_start + tile_size, width)
                
                tile = img_array[y_start:y_end, x_start:x_end]
                hist, _ = np.histogram(tile.flatten(), bins=256, range=(0, 256))
                
                clipped_hist = np.clip(hist, 0, clip_limit * hist.mean())
                excess = np.sum(hist - clipped_hist)
                
                if excess > 0:
                    clipped_hist += excess / 256
                
                cdf = np.cumsum(clipped_hist)
                cdf = cdf / cdf[-1]
                
                lookup_tables[ty, tx] = cdf * 255
        
        result = np.zeros_like(img_array)
        
        for y in range(height):
            for x in range(width):
                tile_y = min(y // tile_size, tiles_y - 1)
                tile_x = min(x // tile_size, tiles_x - 1)
                pixel_val = int(img_array[y, x])
                result[y, x] = lookup_tables[tile_y, tile_x, pixel_val]
        
        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8), mode='L')
    
    def convert_to_ascii(self, image: Image.Image) -> str:
        """Convert an image to ASCII art."""
        width, height = image.size
        ascii_lines = []
        
        for y in range(height):
            line = ""
            for x in range(width):
                pixel_value = image.getpixel((x, y))
                ascii_char = self.pixel_to_ascii(pixel_value)
                line += ascii_char
            ascii_lines.append(line)
        
        return "\n".join(ascii_lines)
    
    def process_image(self, image_path: str, size: Optional[Tuple[int, int]] = None,
                     block_avg: Optional[int] = None, contrast: Optional[float] = None,
                     dither_bayer: Optional[int] = None, dither_error: Optional[str] = None,
                     clahe_clip_limit: Optional[float] = None, clahe_tile_size: Optional[int] = None,
                     use_space: bool = False, maintain_aspect: bool = False) -> str:
        """Process an image file and convert it to ASCII art with optional algorithms."""
        image = self.load_image(image_path)
        image = self.image_to_grayscale(image)
        
        # Apply algorithms in optimal order
        if block_avg:
            image = self.apply_block_averaging(image, block_avg)
        
        if clahe_clip_limit is not None:
            tile_size = clahe_tile_size if clahe_tile_size is not None else 8
            image = self.apply_clahe(image, clahe_clip_limit, tile_size)
        
        if contrast:
            image = self.apply_contrast_shaping(image, contrast)
        
        if dither_bayer:
            image = self.apply_bayer_dithering(image, dither_bayer)
        
        if dither_error:
            image = self.apply_error_diffusion(image, dither_error)
        
        if size:
            image = self.resize_image(image, size, maintain_aspect)
        
        # Create a temporary converter with the space parameter if needed
        if use_space:
            temp_converter = ImageToAsciiConverter(use_space=True)
            return temp_converter.convert_to_ascii(image)
        else:
            return self.convert_to_ascii(image)


def parse_size(size_str: str) -> Tuple[int, int]:
    """Parse size string in format 'WIDTHxHEIGHT'."""
    try:
        width, height = map(int, size_str.split('x'))
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        if width > MAX_WIDTH or height > MAX_HEIGHT:
            raise ValueError(f"Size too large. Maximum allowed: {MAX_WIDTH}x{MAX_HEIGHT}")
        return (width, height)
    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError("Invalid size format. Use 'WIDTHxHEIGHT' (e.g., '80x40')")
        raise


def main():
    """Main function to handle command-line interface."""
    parser = argparse.ArgumentParser(
        description="Convert images to ASCII art",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.png
  %(prog)s image.png -o output.txt
  %(prog)s image.png -s 100x50
  %(prog)s image.png -s 100x50 --maintain-aspect
  %(prog)s image.png --use-space
  %(prog)s image.png --block-avg 3 --contrast 2.0
  %(prog)s image.png --dither-bayer 4
  %(prog)s image.png --dither-error floyd-steinberg
  %(prog)s image.png --clahe-clip-limit 3.0 --clahe-tile-size 6
  %(prog)s image.png --block-avg 2 --clahe-clip-limit 2.5 --contrast 1.5 --dither-error jjn --use-space --maintain-aspect
        """
    )
    
    parser.add_argument(
        'image',
        help='Path to the input image file'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (if not specified, prints to console)'
    )
    
    parser.add_argument(
        '-s', '--size',
        help=f'Resize image to WIDTHxHEIGHT (default: {DEFAULT_SIZE[0]}x{DEFAULT_SIZE[1]}, max: {MAX_WIDTH}x{MAX_HEIGHT})'
    )
    
    parser.add_argument(
        '--block-avg',
        type=int,
        metavar='SIZE',
        help='Apply block averaging with block size (default: 2)'
    )
    
    parser.add_argument(
        '--contrast',
        type=float,
        metavar='STRENGTH',
        help='Apply contrast shaping with strength factor (default: 1.5)'
    )
    
    parser.add_argument(
        '--dither-bayer',
        type=int,
        metavar='SIZE',
        choices=[2, 4, 8],
        help='Apply Bayer dithering with matrix size (2, 4, or 8)'
    )
    
    parser.add_argument(
        '--dither-error',
        type=str,
        metavar='ALGORITHM',
        choices=['floyd-steinberg', 'jjn', 'stucki'],
        help='Apply error-diffusion dithering (floyd-steinberg, jjn, stucki)'
    )
    
    parser.add_argument(
        '--clahe-clip-limit',
        type=float,
        metavar='LIMIT',
        help='Apply CLAHE with clip limit (default: 2.0, higher = more contrast)'
    )
    
    parser.add_argument(
        '--clahe-tile-size',
        type=int,
        metavar='SIZE',
        help='CLAHE tile size (default: 8, smaller = more local adaptation)'
    )
    
    parser.add_argument(
        '--use-space',
        action='store_true',
        help='Use space character for darkest pixels instead of backtick'
    )
    
    parser.add_argument(
        '--maintain-aspect',
        action='store_true',
        help='Maintain original aspect ratio while maximizing size within limits'
    )
    
    args = parser.parse_args()
    
    try:
        size = None
        if args.size:
            size = parse_size(args.size)
        else:
            size = DEFAULT_SIZE
        converter = ImageToAsciiConverter()
        ascii_art = converter.process_image(
            args.image, 
            size=size,
            block_avg=args.block_avg,
            contrast=args.contrast,
            dither_bayer=args.dither_bayer,
            dither_error=args.dither_error,
            clahe_clip_limit=args.clahe_clip_limit,
            clahe_tile_size=args.clahe_tile_size,
            use_space=args.use_space,
            maintain_aspect=args.maintain_aspect
        )
        
        # Output result
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(ascii_art, encoding='utf-8')
            print(f"ASCII art saved to: {output_path}")
        else:
            print(ascii_art)
            
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
