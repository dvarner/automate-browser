#!/usr/bin/env python3
"""
Simple icon generator for Chrome extension.
Creates basic colored placeholder icons.

Usage:
    python create_icons.py
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL/Pillow not installed. Install with: pip install Pillow")
    print("Or create icons manually and place in icons/ folder")

def create_icon(size, output_path):
    """Create a simple gradient icon with text."""
    # Create image with gradient
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)

    # Create gradient background (purple theme matching popup)
    for y in range(size):
        # Purple gradient
        r = int(102 + (118 - 102) * (y / size))
        g = int(126 + (75 - 126) * (y / size))
        b = int(234 + (162 - 234) * (y / size))
        draw.rectangle([(0, y), (size, y + 1)], fill=(r, g, b))

    # Draw icon symbol (download arrow or tabs symbol)
    # Simple representation: Three stacked rectangles (tabs)
    tab_color = (255, 255, 255, 200)  # White with some transparency

    if size >= 48:
        # Draw three tab rectangles
        rect_height = size // 8
        rect_width = int(size * 0.6)
        start_x = (size - rect_width) // 2
        start_y = size // 4
        spacing = rect_height + size // 12

        for i in range(3):
            y_pos = start_y + (i * spacing)
            # Draw rounded rectangle (simplified)
            draw.rectangle(
                [(start_x, y_pos), (start_x + rect_width, y_pos + rect_height)],
                fill=tab_color[:3],
                outline=(255, 255, 255)
            )
    else:
        # For small icons, just draw a simple symbol
        center = size // 2
        rect_size = size // 3
        draw.rectangle(
            [(center - rect_size, center - rect_size),
             (center + rect_size, center + rect_size)],
            fill=(255, 255, 255),
            outline=(255, 255, 255)
        )

    # Save image
    img.save(output_path, 'PNG')
    print(f"Created: {output_path} ({size}x{size})")

def main():
    """Generate all required icon sizes."""
    if not PIL_AVAILABLE:
        return

    import os

    # Ensure icons directory exists
    icons_dir = 'icons'
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)

    # Create icons in required sizes
    sizes = [16, 48, 128]

    for size in sizes:
        output_path = os.path.join(icons_dir, f'icon{size}.png')
        create_icon(size, output_path)

    print("\n✓ All icons created successfully!")
    print("Icons saved to: chrome-extension/icons/")
    print("\nNext steps:")
    print("1. Reload extension in chrome://extensions/")
    print("2. The icons should now appear in your toolbar")
    print("\nOptional: Replace with custom icons if desired")

if __name__ == '__main__':
    main()
