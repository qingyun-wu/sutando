#!/usr/bin/env python3
"""
Image generation and editing using Gemini's native image generation.

Supports:
- Text-to-image: generate from a text prompt
- Image editing: modify an existing image with a text prompt
- Multiple input images for compositing/reference

Usage:
  python3 generate.py --prompt "A sunset over mountains"
  python3 generate.py --input photo.jpg --prompt "Replace the background with a beach"
  python3 generate.py --input bg.jpg --prompt "Add title 'Hello' in large white text" --output hero.png
"""

import argparse
import base64
import os
import sys
import time
from pathlib import Path

def load_env():
    """Load GEMINI_API_KEY from .env files."""
    for env_path in [
        Path(__file__).resolve().parent.parent.parent.parent / ".env",
        Path.home() / ".env",
    ]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())

def main():
    parser = argparse.ArgumentParser(description="Generate or edit images using Gemini")
    parser.add_argument("--prompt", "-p", required=True, help="Text prompt")
    parser.add_argument("--input", "-i", action="append", default=[], help="Input image path(s) for editing (can specify multiple)")
    parser.add_argument("--output", "-o", default=None, help="Output file path (default: generated-{timestamp}.png)")
    parser.add_argument("--model", "-m", default="gemini-2.5-flash-image",
                        help="Gemini model (default: gemini-2.5-flash-image)")
    parser.add_argument("--quality", "-q", type=int, default=90, help="JPEG quality 1-100 (default: 90)")
    args = parser.parse_args()

    load_env()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set. Add it to .env or export it.", file=sys.stderr)
        sys.exit(1)

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai not installed. Run: pip3 install google-genai", file=sys.stderr)
        sys.exit(1)

    try:
        from PIL import Image
        import io
    except ImportError:
        print("Error: Pillow not installed. Run: pip3 install Pillow", file=sys.stderr)
        sys.exit(1)

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Build contents: images first, then prompt
    contents = []

    for img_path in args.input:
        img_path = os.path.expanduser(img_path)
        if not os.path.isfile(img_path):
            print(f"Error: Input image not found: {img_path}", file=sys.stderr)
            sys.exit(1)

        img = Image.open(img_path)

        # Resize if too large (Gemini has limits)
        max_dim = 4096
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            print(f"  Resized {img_path} to {new_size[0]}x{new_size[1]}", file=sys.stderr)

        contents.append(img)
        print(f"  Input: {img_path} ({img.size[0]}x{img.size[1]})", file=sys.stderr)

    contents.append(args.prompt)

    # Determine output path
    if args.output:
        out_path = Path(args.output)
    else:
        ts = int(time.time() * 1000)
        out_path = Path(f"generated-{ts}.png")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine output format
    ext = out_path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        out_format = "JPEG"
    elif ext == ".webp":
        out_format = "WEBP"
    else:
        out_format = "PNG"

    print(f"  Model: {args.model}", file=sys.stderr)
    print(f"  Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}", file=sys.stderr)
    print(f"  Generating...", file=sys.stderr)

    try:
        response = client.models.generate_content(
            model=args.model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
    except Exception as e:
        print(f"Error: Gemini API call failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract image from response
    image_saved = False
    text_response = ""

    if response.candidates:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                # Decode and save
                img_data = part.inline_data.data
                img = Image.open(io.BytesIO(img_data))

                save_kwargs = {}
                if out_format == "JPEG":
                    img = img.convert("RGB")
                    save_kwargs["quality"] = args.quality
                elif out_format == "WEBP":
                    save_kwargs["quality"] = args.quality

                img.save(str(out_path), out_format, **save_kwargs)
                image_saved = True
                print(f"  Saved: {out_path} ({img.size[0]}x{img.size[1]}, {out_format})", file=sys.stderr)
            elif part.text:
                text_response += part.text

    if not image_saved:
        print(f"Error: No image in response.", file=sys.stderr)
        if text_response:
            print(f"  Model said: {text_response}", file=sys.stderr)
        sys.exit(1)

    if text_response:
        print(f"  Note: {text_response.strip()}", file=sys.stderr)

    # Print the output path to stdout (for piping)
    print(str(out_path.resolve()))


if __name__ == "__main__":
    main()
