import io
from pathlib import Path
from PIL import Image

# Directory where main.py resides
BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "static" / "uploads"


def save_image(file_data: bytes, filename: str) -> str:
    """
    Save image bytes to the static/uploads/ directory with Pillow optimization.

    Parameters
    ----------
    file_data : bytes
        Raw bytes of the uploaded image file.
    filename : str
        Destination filename (e.g. "q_1_abc123.jpg").

    Returns
    -------
    str
        Relative path suitable for storing in the database and building
        a URL, e.g. "uploads/q_1_abc123.jpg".
    """
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    image = Image.open(io.BytesIO(file_data))

    # Convert palette / RGBA images to RGB so JPEG encoding always works
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    dest_path = UPLOADS_DIR / filename
    image.save(dest_path, format="JPEG", optimize=True, quality=85)

    return f"uploads/{filename}"
