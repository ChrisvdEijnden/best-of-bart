import os
import tempfile
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

COVER_RATIO = (5, 7)  # width : height, same shape as the gallery tiles


def crop_to_ratio(file, ratio=COVER_RATIO):
    """Center-crop an image to the given width:height ratio.

    Returns a ContentFile with the cropped image, or None if the image
    already has the right shape.
    """
    file.seek(0)
    img = Image.open(file)
    fmt = "JPEG" if img.format in (None, "MPO") else img.format
    # Phone photos are often stored sideways with an EXIF rotation flag.
    img = ImageOps.exif_transpose(img)

    width, height = img.size
    target = ratio[0] / ratio[1]
    if abs(width / height - target) < 0.005:
        return None

    if width / height > target:
        new_width = round(height * target)
        left = (width - new_width) // 2
        img = img.crop((left, 0, left + new_width, height))
    else:
        new_height = round(width / target)
        top = (height - new_height) // 2
        img = img.crop((0, top, width, top + new_height))

    if fmt == "JPEG" and img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    buffer = BytesIO()
    img.save(buffer, format=fmt, **({"quality": 90} if fmt == "JPEG" else {}))
    return ContentFile(buffer.getvalue())


THUMB_WIDTH = 720  # 2x the largest display size (350px popup), ~3x a phone card


def thumbnail_url(image_field, width=THUMB_WIDTH):
    """URL of a downscaled JPEG copy of an uploaded image, made on first use.

    Thumbnails are a disposable cache under media/main/thumbs/ (git-ignored,
    never pushed): delete the folder and they are rebuilt. A thumbnail is
    rebuilt when its source file is newer. Returns None if it can't be made,
    so callers can fall back to the original.
    """
    if not image_field:
        return None
    storage = image_field.storage
    source = Path(image_field.path)
    name = f"main/thumbs/{source.stem}-{source.suffix.lstrip('.').lower()}-{width}.jpg"
    target = Path(storage.path(name))
    try:
        if target.exists() and target.stat().st_mtime >= source.stat().st_mtime:
            _make_public(target)
            return storage.url(name)
        with Image.open(source) as img:
            img = ImageOps.exif_transpose(img)
            img.thumbnail((width, width * 4), Image.LANCZOS)
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGBA")
                background = Image.new("RGB", img.size, "white")
                background.paste(img, mask=img.getchannel("A"))
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")
            target.parent.mkdir(parents=True, exist_ok=True)
            # Write to a temp file and rename, so a parallel request never
            # serves a half-written thumbnail.
            fd, tmp = tempfile.mkstemp(dir=target.parent, suffix=".tmp")
            with os.fdopen(fd, "wb") as out:
                img.save(out, "JPEG", quality=80, optimize=True, progressive=True)
            _make_public(Path(tmp))
            os.replace(tmp, target)
        return storage.url(name)
    except (OSError, ValueError):
        return None


def _make_public(path):
    """Let the web server read the file (and its folder).

    mkstemp creates files readable by their owner only (0600). The web server
    serves /media/ straight from disk as a different user, so without this
    every thumbnail comes back as 403 Forbidden.
    """
    if path.stat().st_mode & 0o777 != 0o644:
        os.chmod(path, 0o644)
    folder = path.parent
    if folder.stat().st_mode & 0o755 != 0o755:
        os.chmod(folder, folder.stat().st_mode | 0o755)
