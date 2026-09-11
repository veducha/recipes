#!/usr/bin/env python3
"""
Process raw recipe submissions into formatted Markdown and hero images.
Uses Google GenAI SDK (Gemini) for text structuring and PIL for image optimization.
"""

import json
import os
import re
import sys
import requests
from io import BytesIO
from PIL import Image, ImageOps

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: 'google-genai' package is required. Install via: pip install google-genai", file=sys.stderr)
    sys.exit(1)


def sanitize_slug(text: str) -> str:
    """Ensure slug is clean kebab-case: lowercase letters, numbers, and hyphens."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "recipe"


def parse_recipe_with_gemini(client: genai.Client, raw_text: str, title: str = "") -> dict:
    """Prompt Gemini to parse raw text into clean markdown matching the repo template."""
    system_instruction = (
        "You are a recipe editor for a minimalist static recipe website. "
        "Your task is to take unformatted recipe text and format it strictly "
        "according to the website's markdown template and conventions."
    )

    title_instruction = f"The user specified the title: '{title}'." if title else "Extract a clean Title Case title from the recipe."

    prompt = f"""
{title_instruction}

Format the recipe text according to this exact structure:

```markdown
# [TITLE]
[Optional one-line subheader / description]

## info  
* About [X] minutes  
* [X] servings  

## ingredients
* [ingredient with quantity and preparation]
* ...

## steps  
1. [Clear numbered instruction step]
2. ...

## notes  
* [Any tips, substitutions, or variations; omit section if none]

## based on  
* [Source or author if mentioned in text; omit section if none]
```

Formatting rules:
- Top heading `# [TITLE]` must match the recipe title.
- If servings or time are not specified, estimate reasonably or use 'N/A'.
- Keep step instructions clear, concise, and numbered.
- Under 'info', end each line with two spaces before the newline for markdown line breaks.
- Return the final title, kebab-case slug, and formatted markdown.

Recipe text:
\"\"\"
{raw_text}
\"\"\"
"""

    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "slug": {"type": "string"},
                    "markdown": {"type": "string"},
                },
                "required": ["title", "slug", "markdown"],
            },
        ),
    )

    data = json.loads(response.text)
    effective_title = title if title else data.get("title", "New Recipe")
    data["title"] = effective_title
    data["slug"] = sanitize_slug(effective_title)
    return data


def download_and_save_image(url: str, output_path: str):
    """Download an uploaded image (supports Google Drive and direct URLs), convert to JPG, and save."""
    print(f"Downloading uploaded recipe image from: {url}")
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # If it's a Google Drive export link, handle potential confirmation cookies
    resp = session.get(url, headers=headers, timeout=30, stream=True)
    resp.raise_for_status()

    # Google Drive sometimes sends a confirmation page for large files
    for key, value in resp.cookies.items():
        if key.startswith("download_warning"):
            resp = session.get(f"{url}&confirm={value}", headers=headers, timeout=30, stream=True)
            break

    img = Image.open(BytesIO(resp.content))

    # Convert to RGB (in case of PNG with transparency or HEIC/RGBA)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # If image is taller than 16:9 (e.g. square, portrait, 4:3), center-crop to banner
    aspect_ratio = img.width / img.height
    if aspect_ratio < 1.7:
        target_height = int(img.width / (16 / 9))
        img = ImageOps.fit(img, (img.width, target_height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

    # Resize if excessively large to keep git repo lean (max width 1600px)
    max_dim = 1600
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    img.save(output_path, format="JPEG", quality=85, optimize=True)
    print(f"Saved hero image to {output_path}")


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    recipe_title = os.environ.get("RECIPE_TITLE", "").strip()
    raw_recipe = os.environ.get("RECIPE_TEXT", "").strip()
    image_url = os.environ.get("IMAGE_URL", "").strip()

    if not raw_recipe:
        print("Error: RECIPE_TEXT is empty. Nothing to process.", file=sys.stderr)
        sys.exit(1)

    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    recipes_dir = os.path.join(repo_dir, "recipes")
    images_dir = os.path.join(repo_dir, "images")
    os.makedirs(recipes_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    client = genai.Client(api_key=api_key)

    print("Sending recipe text to Gemini...")
    parsed = parse_recipe_with_gemini(client, raw_recipe, recipe_title)

    slug = parsed["slug"]
    markdown_content = parsed["markdown"].strip() + "\n"

    # Write recipe markdown
    md_filename = f"{slug}.md"
    md_path = os.path.join(recipes_dir, md_filename)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Wrote recipe markdown to {md_path}")

    # Handle the uploaded image
    if image_url:
        image_filename = f"{slug}.jpg"
        image_path = os.path.join(images_dir, image_filename)
        try:
            download_and_save_image(image_url, image_path)
        except Exception as e:
            print(f"Warning: Failed to download or convert uploaded image ({e}). Skipping image.", file=sys.stderr)
    else:
        print("No image provided with this submission.")

    # Write slug to .recipe_slug for GitHub Actions workflow
    slug_file = os.path.join(repo_dir, ".recipe_slug")
    with open(slug_file, "w", encoding="utf-8") as f:
        f.write(slug)
    print(f"Saved slug '{slug}' to {slug_file}")


if __name__ == "__main__":
    main()
