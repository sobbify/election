import os
import string
import random
from pathlib import Path
from PIL import Image
from io import BytesIO

# Image storage directory
IMAGES_DIR = Path(__file__).parent / "static" / "uploads"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def generate_random_token(length: int = 5) -> str:
    """Generate a random alphanumeric token."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def save_image(file_data: bytes, filename: str) -> str:
    """Save image file with optimization and return the relative path."""
    try:
        # Open image with PIL to validate and optimize
        img = Image.open(BytesIO(file_data))
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Resize if too large (max 800x600)
        img.thumbnail((800, 600), Image.Resampling.LANCZOS)
        
        # Save with compression (JPEG for better compatibility)
        filepath = IMAGES_DIR / filename
        img.save(filepath, 'JPEG', quality=75, optimize=True)
        
        return f"/static/uploads/{filename}"
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def delete_image(image_path: str) -> bool:
    """Delete an image file."""
    if not image_path:
        return False
    try:
        filepath = Path(__file__).parent / image_path.lstrip('/')
        if filepath.exists():
            filepath.unlink()
            return True
    except Exception as e:
        print(f"Error deleting image: {e}")
    return False
