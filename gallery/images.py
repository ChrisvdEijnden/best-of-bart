from io import BytesIO

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
