---
name: image-generation
description: "Generate and edit images using Gemini's native image generation. Supports text-to-image, image editing with text prompts, background replacement, text overlay, style transfer, and more. Input can be text-only or text + image."
---

# Image Generation

Generate and edit images using Gemini 2.5 Flash Image API. Supports:
- **Text-to-image**: Generate images from text descriptions
- **Image editing**: Modify existing images with natural language
- **Background replacement**: Change or enhance backgrounds
- **Hero/banner creation**: Create branded images with text overlays
- **Style transfer**: Apply artistic styles to photos

## When to Use

- "Generate a hero image for my project"
- "Replace the background with a sunset"
- "Add text overlay to this image"
- "Create a logo with a dark theme"
- "Edit this photo to remove the person"
- "Make this image look like a watercolor painting"

## Usage

```bash
# Text-to-image generation
python3 "$SKILL_DIR/scripts/generate.py" --prompt "A futuristic city skyline at night"

# Edit an existing image
python3 "$SKILL_DIR/scripts/generate.py" --input photo.jpg --prompt "Add dramatic clouds to the sky"

# Generate a hero banner from a background image
python3 "$SKILL_DIR/scripts/generate.py" --input background.jpg \
  --prompt "Create a hero banner with title text and subtitle. Dark gradient overlay for readability." \
  --output hero.jpg

# Specify output path
python3 "$SKILL_DIR/scripts/generate.py" --prompt "A cute robot mascot" --output mascot.png

# Specify model
python3 "$SKILL_DIR/scripts/generate.py" --prompt "Abstract art" --model gemini-2.5-flash-image
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--prompt` | Text prompt describing what to generate/edit | (required) |
| `--input` | Input image path (for editing) | None (text-to-image) |
| `--output` | Output file path | `generated-{timestamp}.png` |
| `--model` | Gemini model to use | `gemini-2.5-flash-image` |
| `--quality` | JPEG quality (1-100) | 90 |

## Requirements

- `google-genai` Python package (`pip3 install google-genai`)
- `GEMINI_API_KEY` in `.env` or environment
- Pillow (`pip3 install Pillow`)

## Notes

- Gemini may refuse some prompts (people's faces, copyrighted characters, etc.)
- For best results with image editing, be explicit: "keep the subject unchanged, only modify the background"
- Output format is inferred from the output path extension (.jpg, .png, .webp)
- Maximum input image size: ~20MB
