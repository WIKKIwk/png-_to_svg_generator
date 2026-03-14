#!/usr/bin/env python3
"""
PNG to SVG Converter
====================
Converts PNG images to high-quality SVG vector format.
Uses edge detection and contour tracing to create clean vector paths.
"""

import os
import sys
import math
from PIL import Image
import numpy as np


def png_to_svg_traced(input_path, output_path, threshold=200, smoothing=1.0):
    """
    Convert a PNG image to SVG using contour tracing.
    
    This method:
    1. Converts the image to grayscale
    2. Applies thresholding to create a binary image
    3. Detects edges using simple edge detection
    4. Traces contours and converts them to SVG paths
    
    Args:
        input_path: Path to the input PNG file
        output_path: Path to save the output SVG file
        threshold: Grayscale threshold for binary conversion (0-255)
        smoothing: Path smoothing factor (0.0 to 2.0)
    """
    print(f"  Loading image: {input_path}")
    img = Image.open(input_path)
    
    # Handle transparency - composite on white background
    if img.mode == 'RGBA':
        background = Image.new('RGBA', img.size, (255, 255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background.convert('L')
    elif img.mode != 'L':
        img = img.convert('L')
    
    width, height = img.size
    pixels = np.array(img)
    
    print(f"  Image size: {width}x{height}")
    print(f"  Threshold: {threshold}, Smoothing: {smoothing}")
    
    # Apply threshold to create binary image
    binary = (pixels < threshold).astype(np.uint8)
    
    # Find edges using simple gradient detection
    edges = find_edges(binary)
    
    # Trace contours from edges
    contours = trace_contours(edges)
    
    # Simplify and smooth contours
    simplified_contours = []
    for contour in contours:
        if len(contour) >= 3:
            simplified = simplify_path(contour, tolerance=smoothing)
            if len(simplified) >= 3:
                simplified_contours.append(simplified)
    
    print(f"  Found {len(simplified_contours)} contours")
    
    # Generate SVG
    svg_content = generate_svg(width, height, simplified_contours)
    
    # Write SVG file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    file_size = os.path.getsize(output_path)
    print(f"  SVG saved: {output_path} ({file_size:,} bytes)")
    return True


def find_edges(binary):
    """
    Find edges in a binary image using simple gradient detection.
    Returns a 2D array where edge pixels are marked as 1.
    """
    h, w = binary.shape
    edges = np.zeros_like(binary)
    
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if binary[y, x] == 1:
                # Check if any neighbor is 0 (background)
                neighbors = [
                    binary[y-1, x], binary[y+1, x],
                    binary[y, x-1], binary[y, x+1],
                    binary[y-1, x-1], binary[y-1, x+1],
                    binary[y+1, x-1], binary[y+1, x+1]
                ]
                if 0 in neighbors:
                    edges[y, x] = 1
    
    return edges


def trace_contours(edges):
    """
    Trace contours from edge image using a simple boundary following algorithm.
    Returns a list of contours, where each contour is a list of (x, y) points.
    """
    h, w = edges.shape
    visited = np.zeros_like(edges)
    contours = []
    
    # Direction vectors for 8-connectivity (clockwise from right)
    dx = [1, 1, 0, -1, -1, -1, 0, 1]
    dy = [0, 1, 1, 1, 0, -1, -1, -1]
    
    for y in range(h):
        for x in range(w):
            if edges[y, x] == 1 and visited[y, x] == 0:
                contour = trace_single_contour(edges, visited, x, y, dx, dy, w, h)
                if len(contour) >= 5:
                    contours.append(contour)
    
    return contours


def trace_single_contour(edges, visited, start_x, start_y, dx, dy, w, h):
    """
    Trace a single contour starting from (start_x, start_y).
    Uses Moore neighborhood tracing algorithm.
    """
    contour = [(start_x, start_y)]
    visited[start_y, start_x] = 1
    
    cx, cy = start_x, start_y
    direction = 0
    max_steps = w * h  # Safety limit
    
    for _ in range(max_steps):
        found = False
        # Search in 8 directions starting from current direction
        for i in range(8):
            d = (direction + i) % 8
            nx, ny = cx + dx[d], cy + dy[d]
            
            if 0 <= nx < w and 0 <= ny < h:
                if edges[ny, nx] == 1 and visited[ny, nx] == 0:
                    visited[ny, nx] = 1
                    contour.append((nx, ny))
                    cx, cy = nx, ny
                    direction = (d + 5) % 8  # Turn back slightly
                    found = True
                    break
        
        if not found:
            break
        
        # Check if we're back to start
        if abs(cx - start_x) <= 1 and abs(cy - start_y) <= 1 and len(contour) > 10:
            contour.append((start_x, start_y))
            break
    
    return contour


def simplify_path(points, tolerance=1.0):
    """
    Simplify a path using the Ramer-Douglas-Peucker algorithm.
    This reduces the number of points while preserving shape.
    """
    if len(points) <= 2:
        return points
    
    # Find the point farthest from the line between first and last
    start = points[0]
    end = points[-1]
    
    max_dist = 0
    max_idx = 0
    
    for i in range(1, len(points) - 1):
        dist = point_to_line_distance(points[i], start, end)
        if dist > max_dist:
            max_dist = dist
            max_idx = i
    
    # If max distance is greater than tolerance, recursively simplify
    if max_dist > tolerance:
        left = simplify_path(points[:max_idx + 1], tolerance)
        right = simplify_path(points[max_idx:], tolerance)
        return left[:-1] + right
    else:
        return [start, end]


def point_to_line_distance(point, line_start, line_end):
    """Calculate perpendicular distance from a point to a line segment."""
    px, py = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    dx = x2 - x1
    dy = y2 - y1
    
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
    
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / length_sq))
    
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    
    return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)


def generate_svg(width, height, contours):
    """
    Generate SVG markup from contours.
    Uses quadratic bezier curves for smooth paths.
    """
    paths = []
    
    for contour in contours:
        if len(contour) < 3:
            continue
        
        # Build SVG path data with smooth curves
        path_data = f"M {contour[0][0]},{contour[0][1]}"
        
        i = 1
        while i < len(contour) - 1:
            # Use quadratic bezier for smoothing
            cx, cy = contour[i]
            nx, ny = contour[i + 1] if i + 1 < len(contour) else contour[i]
            
            # Midpoint for smooth transition
            mx = (cx + nx) / 2
            my = (cy + ny) / 2
            
            path_data += f" Q {cx},{cy} {mx},{my}"
            i += 1
        
        # Close path if endpoints are close
        if len(contour) > 2:
            last = contour[-1]
            first = contour[0]
            dist = math.sqrt((last[0] - first[0])**2 + (last[1] - first[1])**2)
            if dist < 5:
                path_data += " Z"
            else:
                path_data += f" L {last[0]},{last[1]}"
        
        paths.append(path_data)
    
    # Build SVG document
    svg_parts = [
        f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg"',
        f'     width="{width}" height="{height}"',
        f'     viewBox="0 0 {width} {height}">',
        f'  <title>Converted from PNG</title>',
        f'  <desc>Generated by PNG to SVG Generator</desc>',
        f'  <g fill="none" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">',
    ]
    
    for path_data in paths:
        svg_parts.append(f'    <path d="{path_data}"/>')
    
    svg_parts.append('  </g>')
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)


def png_to_svg_embedded(input_path, output_path):
    """
    Alternative method: Embed the PNG image inside an SVG.
    This preserves 100% quality but doesn't create true vector paths.
    Useful as a fallback or for complex photographic images.
    """
    import base64
    
    img = Image.open(input_path)
    width, height = img.size
    
    # Read original PNG bytes
    with open(input_path, 'rb') as f:
        png_data = f.read()
    
    b64_data = base64.b64encode(png_data).decode('utf-8')
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <title>Embedded PNG in SVG</title>
  <desc>Original PNG preserved at full quality inside SVG container</desc>
  <image width="{width}" height="{height}"
         href="data:image/png;base64,{b64_data}"/>
</svg>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    file_size = os.path.getsize(output_path)
    print(f"  Embedded SVG saved: {output_path} ({file_size:,} bytes)")
    return True


def convert_all_pngs(input_dir='.', output_dir='output'):
    """
    Convert all PNG files in the input directory to SVG.
    Creates both traced and embedded versions for comparison.
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'traced'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'embedded'), exist_ok=True)
    
    # Find all PNG files
    png_files = [f for f in os.listdir(input_dir) 
                 if f.lower().endswith('.png') and os.path.isfile(os.path.join(input_dir, f))]
    
    if not png_files:
        print("❌ No PNG files found in the current directory!")
        return
    
    print(f"\n{'='*60}")
    print(f"  PNG to SVG Generator")
    print(f"  Found {len(png_files)} PNG file(s)")
    print(f"{'='*60}\n")
    
    success_count = 0
    
    for i, png_file in enumerate(png_files, 1):
        input_path = os.path.join(input_dir, png_file)
        base_name = os.path.splitext(png_file)[0]
        
        # Clean filename for output
        clean_name = base_name.replace(' ', '_')
        
        print(f"\n[{i}/{len(png_files)}] Converting: {png_file}")
        print(f"  {'─'*50}")
        
        # Method 1: Traced SVG (true vector)
        traced_output = os.path.join(output_dir, 'traced', f'{clean_name}_traced.svg')
        try:
            print(f"\n  📐 Method 1: Contour Tracing (True Vector)")
            png_to_svg_traced(input_path, traced_output, threshold=180, smoothing=1.5)
            print(f"  ✅ Traced SVG created successfully!")
        except Exception as e:
            print(f"  ⚠️  Tracing failed: {e}")
        
        # Method 2: Embedded SVG (lossless quality)
        embedded_output = os.path.join(output_dir, 'embedded', f'{clean_name}_embedded.svg')
        try:
            print(f"\n  🖼️  Method 2: Embedded PNG (Lossless Quality)")
            png_to_svg_embedded(input_path, embedded_output)
            print(f"  ✅ Embedded SVG created successfully!")
        except Exception as e:
            print(f"  ⚠️  Embedding failed: {e}")
        
        success_count += 1
    
    print(f"\n{'='*60}")
    print(f"  ✅ Conversion complete!")
    print(f"  Converted: {success_count}/{len(png_files)} files")
    print(f"  Output directory: {output_dir}/")
    print(f"    ├── traced/    (true vector SVGs)")
    print(f"    └── embedded/  (lossless quality SVGs)")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    # Get script directory as working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    convert_all_pngs(
        input_dir='.',
        output_dir='output'
    )
