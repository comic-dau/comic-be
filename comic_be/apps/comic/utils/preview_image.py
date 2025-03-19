from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


def create_preview_image(image):
    img = Image.open(image)
    img = img.convert("RGB")
    img.thumbnail((384, 512))
    img_io = BytesIO()
    img.save(img_io, format="JPEG", )
    return ContentFile(img_io.getvalue(), name=f"p_{image.name}")
