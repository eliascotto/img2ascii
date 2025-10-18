#!/usr/bin/env python3
"""Example script demonstrating img2ascii usage."""

import sys
from pathlib import Path

# Add current directory to path
current_path = Path(__file__).parent
sys.path.insert(0, str(current_path))

from img2ascii import ImageToAsciiConverter


def main():
    """Demonstrate usage of the ImageToAsciiConverter with different algorithms."""
    print("img2ascii Algorithm Comparison")
    print("=" * 50)
    
    # Check if image path is provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python algorithm_comparison.py <image_path>")
        print("Example: python algorithm_comparison.py photo.jpg")
        return
    
    image_path = sys.argv[1]
    
    # Check if the image file exists
    if not Path(image_path).exists():
        print(f"Error: Image file '{image_path}' not found.")
        return
    
    print(f"Converting: {image_path}")
    
    try:
        converter = ImageToAsciiConverter()
        size = (60, 30)  # Consistent size for comparison
        
        # Basic conversion
        print("\n1. Basic Conversion:")
        print("-" * 30)
        ascii_art = converter.process_image(image_path, size=size)
        print(ascii_art)

        print("\n2. Use space:")
        print("-" * 30)
        ascii_art = converter.process_image(image_path, size=size, use_space=True)
        print(ascii_art)
        
        # Block averaging
        print("\n3. Block Averaging (block size 3):")
        print("-" * 30)
        ascii_art = converter.process_image(image_path, size=size, block_avg=3, use_space=True)
        print(ascii_art)
        
        # Contrast shaping
        print("\n4. Contrast Shaping (strength 0.5):")
        print("-" * 30)
        ascii_art = converter.process_image(image_path, size=size, contrast=0.5, use_space=True)
        print(ascii_art)
        
        # CLAHE
        print("\n5. CLAHE (clip limit 3.0, tile size 6):")
        print("-" * 30)
        ascii_art = converter.process_image(image_path, size=size, clahe_clip_limit=3.0, clahe_tile_size=6, use_space=True)
        print(ascii_art)
        
        # Bayer dithering
        print("\n6. Bayer Dithering (4x4 matrix):")
        print("-" * 30)
        ascii_art = converter.process_image(image_path, size=size, dither_bayer=4, use_space=True)
        print(ascii_art)
        
        # Error diffusion
        print("\n7. Floyd-Steinberg Error Diffusion:")
        print("-" * 30)
        ascii_art = converter.process_image(image_path, size=size, dither_error='floyd-steinberg', use_space=True)
        print(ascii_art)
        
        # Combined algorithms
        print("\n8. Combined: Block Avg + CLAHE + Contrast + JJN Dithering:")
        print("-" * 30)
        ascii_art = converter.process_image(
            image_path, 
            size=size, 
            block_avg=2, 
            clahe_clip_limit=2,
            clahe_tile_size=4,
            contrast=0.5, 
            dither_error='jjn',
            use_space=True
        )
        print(ascii_art)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
