"""Basic image enhancement tool using Pillow.

Applies manual enhancement factors in order:
Brightness -> Contrast -> Sharpness -> Color.
"""

import argparse
import os
import sys

from PIL import Image, ImageEnhance


def enhance_image(
    input_path, output_path, brightness=1.0, contrast=1.0, sharpness=1.0, color=1.0
):
    """Enhance an image with the given factors and save to output_path.

    Args:
        input_path: Path to input image.
        output_path: Path to save enhanced image.
        brightness: Brightness factor (1.0 = original, >1 brighter).
        contrast: Contrast factor (1.0 = original).
        sharpness: Sharpness factor (1.0 = original, >1 sharper).
        color: Color balance factor (1.0 = original, 0.0 = grayscale).

    Returns:
        True on success, False on failure.
    """
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} does not exist.")
        return False

    for name, value in [
        ("brightness", brightness),
        ("contrast", contrast),
        ("sharpness", sharpness),
        ("color", color),
    ]:
        if value < 0:
            print(f"Error: --{name} must be >= 0 (got {value}).")
            return False

    try:
        with Image.open(input_path) as img:
            width, height = img.size
            print("================================")
            print("IMAGE ENHANCEMENT REPORT")
            print("================================")
            print(f"Input           : {input_path}")
            print(f"Size            : {width}x{height} px")
            print(f"Mode            : {img.mode}")
            print(f"Brightness      : {brightness}")
            print(f"Contrast        : {contrast}")
            print(f"Sharpness       : {sharpness}")
            print(f"Color           : {color}")

            enhanced = img
            if brightness != 1.0:
                enhanced = ImageEnhance.Brightness(enhanced).enhance(brightness)
            if contrast != 1.0:
                enhanced = ImageEnhance.Contrast(enhanced).enhance(contrast)
            if sharpness != 1.0:
                enhanced = ImageEnhance.Sharpness(enhanced).enhance(sharpness)
            if color != 1.0:
                if enhanced.mode in ("L", "LA", "P"):
                    print("Note: skipping color enhancement for non-color image.")
                else:
                    if enhanced.mode == "RGBA":
                        # Enhance RGB, preserve alpha
                        rgb = enhanced.convert("RGB")
                        rgb = ImageEnhance.Color(rgb).enhance(color)
                        r, g, b = rgb.split()
                        _, _, _, a = enhanced.split()
                        enhanced = Image.merge("RGBA", (r, g, b, a))
                    else:
                        enhanced = ImageEnhance.Color(enhanced).enhance(color)

            enhanced.save(output_path)
            print(f"Output          : {output_path}")
            print("Done.")
            return True
    except Exception as e:
        print(f"Error enhancing image: {e}")
        return False


def parse_args(args=None):
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Basic image enhancement tool (Pillow only)."
    )
    parser.add_argument("input", help="Path to input image")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output path (default: enhanced_<input_name>)",
    )
    parser.add_argument(
        "--brightness",
        type=float,
        default=1.0,
        help="Brightness factor, 1.0 = original (default: 1.0)",
    )
    parser.add_argument(
        "--contrast",
        type=float,
        default=1.0,
        help="Contrast factor, 1.0 = original (default: 1.0)",
    )
    parser.add_argument(
        "--sharpness",
        type=float,
        default=1.0,
        help="Sharpness factor, 1.0 = original (default: 1.0)",
    )
    parser.add_argument(
        "--color",
        type=float,
        default=1.0,
        help="Color factor, 1.0 = original, 0.0 = B&W (default: 1.0)",
    )
    parsed = parser.parse_args(args)

    if parsed.output is None:
        base = os.path.basename(parsed.input)
        name, ext = os.path.splitext(base)
        ext = ext if ext else ".jpg"
        parsed.output = f"enhanced_{name}{ext}"

    return parsed


if __name__ == "__main__":
    opts = parse_args()
    ok = enhance_image(
        opts.input,
        opts.output,
        brightness=opts.brightness,
        contrast=opts.contrast,
        sharpness=opts.sharpness,
        color=opts.color,
    )
    sys.exit(0 if ok else 1)
