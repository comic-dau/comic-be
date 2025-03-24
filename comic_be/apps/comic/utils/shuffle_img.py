import hashlib
from io import BytesIO

import numpy as np
from PIL import Image


def generate_shuffle_indices(key: str, num_pieces: int = 16):
    """Tạo danh sách chỉ mục xáo trộn dựa trên key."""
    hash_val = hashlib.sha256(key.encode()).hexdigest()
    indices = list(range(num_pieces))  # Danh sách các index (0 đến num_pieces - 1)
    np.random.seed(int(hash_val[:8], 16))  # Seed dựa trên key
    np.random.shuffle(indices)  # Xáo trộn danh sách
    return indices


def split_and_shuffle_image(content_file_image, key):
    image_data = content_file_image.read()
    img = Image.open(BytesIO(image_data))
    width, height = img.size
    w, h = width // 4, height // 4

    parts = [img.crop((i * w, j * h, (i + 1) * w, (j + 1) * h)) for j in range(4) for i in range(4)]

    indices = generate_shuffle_indices(key, num_pieces=16)
    shuffled_parts = [parts[i] for i in indices]

    # Tạo ảnh mới từ các phần đã xáo trộn
    new_img = Image.new("RGB", (width, height))
    for idx, part in enumerate(shuffled_parts):
        i, j = divmod(idx, 4)
        new_img.paste(part, (j * w, i * h))

    # Chuyển ảnh thành file object để có thể upload trực tiếp
    buffer = BytesIO()
    new_img.save(buffer, format="PNG")
    buffer.seek(0)  # Reset vị trí đọc về đầu file

    return buffer

def restore_image(shuffled_image_path, key, output_path="restored.png"):
    """Ghép ảnh lại như ban đầu dựa trên key."""
    shuffled_img = Image.open(shuffled_image_path)
    width, height = shuffled_img.size
    w, h = width // 4, height // 2

    indices = generate_shuffle_indices(key)
    restore_indices = np.argsort(indices)  # Lấy lại thứ tự ban đầu

    parts = [shuffled_img.crop((i * w, j * h, (i + 1) * w, (j + 1) * h)) for j in range(2) for i in range(4)]
    restored_parts = [parts[i] for i in restore_indices]

    new_img = Image.new("RGB", (width, height))
    for idx, part in enumerate(restored_parts):
        i, j = divmod(idx, 4)
        new_img.paste(part, (j * w, i * h))

    new_img.save(output_path)


key = "jakscnboascijic___qhui3wjbdf21ie13hroi3rhoi3h1ofjn1qddcbr32r34rt4trfhboasdcbj"

# a = split_and_shuffle_image('/home/viet/Desktop/dau/comic/comic_be/test/image/lavie-350ml.png', key, output_prefix="lavie-350ml")
#
# restore_image('/home/viet/Desktop/dau/comic/comic_be/test/lavie-350ml.png', 'jakscnboascijic___qhui3wjbdf21ie13hroi3rhoi3h1ofjn1qddcbr32r34rt4trfhboasdcbj',
#               '/home/viet/Desktop/dau/comic/comic_be/test/image_result/lavie-350ml.png')

