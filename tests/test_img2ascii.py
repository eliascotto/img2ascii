#!/usr/bin/env python3
"""Tests for img2ascii module."""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from img2ascii import ImageToAsciiConverter, parse_size, ASCII_RAMP


class TestImageToAsciiConverter(unittest.TestCase):
    """Test cases for ImageToAsciiConverter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = ImageToAsciiConverter()
        self.test_image = self._create_test_image()
    
    def _create_test_image(self, width=10, height=10, mode='L'):
        """Create a test image for testing purposes."""
        # Create a simple gradient image
        image = Image.new(mode, (width, height))
        pixels = []
        for y in range(height):
            for x in range(width):
                # Create a gradient from black to white
                value = int((x + y) * 255 / (width + height - 2))
                pixels.append(value)
        image.putdata(pixels)
        return image
    
    def test_init_with_default_ramp(self):
        """Test initialization with default ASCII ramp."""
        converter = ImageToAsciiConverter()
        self.assertEqual(converter.ascii_ramp, ASCII_RAMP)
        self.assertEqual(converter.ramp_length, len(ASCII_RAMP))
    
    def test_init_with_custom_ramp(self):
        """Test initialization with custom ASCII ramp."""
        custom_ramp = "@#$%"
        converter = ImageToAsciiConverter(custom_ramp)
        self.assertEqual(converter.ascii_ramp, custom_ramp)
        self.assertEqual(converter.ramp_length, 4)
    
    def test_load_image_success(self):
        """Test successful image loading."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            self.test_image.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            loaded_image = self.converter.load_image(tmp_path)
            self.assertIsInstance(loaded_image, Image.Image)
            self.assertEqual(loaded_image.size, self.test_image.size)
        finally:
            os.unlink(tmp_path)
    
    def test_load_image_file_not_found(self):
        """Test loading non-existent image file."""
        with self.assertRaises(FileNotFoundError):
            self.converter.load_image("nonexistent.png")
    
    def test_load_image_invalid_file(self):
        """Test loading invalid image file."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b"not an image")
            tmp_path = tmp.name
        
        try:
            with self.assertRaises(ValueError):
                self.converter.load_image(tmp_path)
        finally:
            os.unlink(tmp_path)
    
    def test_resize_image(self):
        """Test image resizing."""
        original_size = (20, 20)
        new_size = (10, 10)
        image = self._create_test_image(*original_size)
        
        resized = self.converter.resize_image(image, new_size)
        self.assertEqual(resized.size, new_size)
    
    def test_image_to_grayscale_already_grayscale(self):
        """Test converting already grayscale image."""
        grayscale_image = self._create_test_image(mode='L')
        result = self.converter.image_to_grayscale(grayscale_image)
        self.assertEqual(result.mode, 'L')
        self.assertEqual(result.size, grayscale_image.size)
    
    def test_image_to_grayscale_rgb(self):
        """Test converting RGB image to grayscale."""
        rgb_image = self._create_test_image(mode='RGB')
        result = self.converter.image_to_grayscale(rgb_image)
        self.assertEqual(result.mode, 'L')
        self.assertEqual(result.size, rgb_image.size)
    
    def test_pixel_to_ascii_dark_pixel(self):
        """Test converting dark pixel to ASCII."""
        # Dark pixel (value 0) should map to first character in ramp
        ascii_char = self.converter.pixel_to_ascii(0)
        self.assertEqual(ascii_char, ASCII_RAMP[0])
    
    def test_pixel_to_ascii_bright_pixel(self):
        """Test converting bright pixel to ASCII."""
        # Bright pixel (value 255) should map to last character in ramp
        ascii_char = self.converter.pixel_to_ascii(255)
        self.assertEqual(ascii_char, ASCII_RAMP[-1])
    
    def test_pixel_to_ascii_middle_pixel(self):
        """Test converting middle brightness pixel to ASCII."""
        # Middle pixel (value 127) should map to middle character in ramp
        ascii_char = self.converter.pixel_to_ascii(127)
        expected_index = int((127 / 255.0) * (len(ASCII_RAMP) - 1))
        self.assertEqual(ascii_char, ASCII_RAMP[expected_index])
    
    def test_convert_to_ascii(self):
        """Test converting image to ASCII art."""
        # Create a simple 2x2 test image
        test_image = self._create_test_image(2, 2)
        ascii_result = self.converter.convert_to_ascii(test_image)
        
        # Should have 2 lines (height)
        lines = ascii_result.split('\n')
        self.assertEqual(len(lines), 2)
        
        # Each line should have 2 characters (width)
        for line in lines:
            self.assertEqual(len(line), 2)
    
    def test_process_image_with_resize(self):
        """Test processing image with resizing."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            self.test_image.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            result = self.converter.process_image(tmp_path, (5, 5))
            lines = result.split('\n')
            self.assertEqual(len(lines), 5)  # Height
            for line in lines:
                self.assertEqual(len(line), 5)  # Width
        finally:
            os.unlink(tmp_path)
    
    def test_process_image_without_resize(self):
        """Test processing image without resizing."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            self.test_image.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            result = self.converter.process_image(tmp_path)
            lines = result.split('\n')
            self.assertEqual(len(lines), self.test_image.height)
            for line in lines:
                self.assertEqual(len(line), self.test_image.width)
        finally:
            os.unlink(tmp_path)


class TestParseSize(unittest.TestCase):
    """Test cases for parse_size function."""
    
    def test_parse_size_valid(self):
        """Test parsing valid size string."""
        size = parse_size("80x40")
        self.assertEqual(size, (80, 40))
    
    def test_parse_size_single_digit(self):
        """Test parsing single digit dimensions."""
        size = parse_size("5x5")
        self.assertEqual(size, (5, 5))
    
    def test_parse_size_large_dimensions(self):
        """Test parsing large dimensions."""
        size = parse_size("200x200")
        self.assertEqual(size, (200, 200))
    
    def test_parse_size_invalid_format(self):
        """Test parsing invalid size format."""
        with self.assertRaises(ValueError):
            parse_size("80-40")
        
        with self.assertRaises(ValueError):
            parse_size("80")
        
        with self.assertRaises(ValueError):
            parse_size("80x")
    
    def test_parse_size_non_numeric(self):
        """Test parsing non-numeric size."""
        with self.assertRaises(ValueError):
            parse_size("abcxdef")
    
    def test_parse_size_zero_dimensions(self):
        """Test parsing zero dimensions."""
        with self.assertRaises(ValueError):
            parse_size("0x40")
        
        with self.assertRaises(ValueError):
            parse_size("80x0")
    
    def test_parse_size_negative_dimensions(self):
        """Test parsing negative dimensions."""
        with self.assertRaises(ValueError):
            parse_size("-80x40")
        
        with self.assertRaises(ValueError):
            parse_size("80x-40")
    
    def test_parse_size_too_large(self):
        """Test parsing dimensions that are too large."""
        with self.assertRaises(ValueError):
            parse_size("201x200")
        
        with self.assertRaises(ValueError):
            parse_size("200x201")


class TestConstants(unittest.TestCase):
    """Test cases for module constants."""
    
    def test_ascii_ramp_length(self):
        """Test that ASCII ramp has reasonable length."""
        self.assertGreater(len(ASCII_RAMP), 10)
        self.assertLess(len(ASCII_RAMP), 100)
    
    def test_ascii_ramp_characters(self):
        """Test that ASCII ramp contains valid characters."""
        for char in ASCII_RAMP:
            self.assertIsInstance(char, str)
            self.assertEqual(len(char), 1)


if __name__ == '__main__':
    unittest.main()
