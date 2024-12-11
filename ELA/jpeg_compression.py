import numpy as np
from PIL import Image, ImageChops, ImageEnhance


def computeForward2DDCT(block):
    """Tính DCT 2D cho khối 8x8"""
    N = block.shape[0]
    dct_block = np.zeros_like(block, dtype=float)
    for u in range(N):
        for v in range(N):
            sum_ = 0
            for x in range(N):
                for y in range(N):
                    sum_ += block[x, y] * np.cos((2 * x + 1) * u * np.pi / (2 * N)) * np.cos((2 * y + 1) * v * np.pi / (2 * N))
            c_u = 1 / np.sqrt(2) if u == 0 else 1
            c_v = 1 / np.sqrt(2) if v == 0 else 1
            dct_block[u, v] = 0.25 * c_u * c_v * sum_
    return dct_block


def quantizeDCTImage(dctImge, Q):
    """Lượng tử hóa ảnh DCT theo ma trận lượng tử hóa Q."""
    N = dctImge.shape[0]
    blockN = Q.shape[0]
    qDctImge = np.zeros([N, N], dtype=int)
    for i in np.arange(0, N, 8):
        for j in np.arange(0, N, 8):
            qDctImge[i:(i + blockN), j:(j + blockN)] = np.round(dctImge[i:(i + blockN), j:(j + blockN)] / Q)
    return qDctImge


def perform_ela(image, jpeg_quality, error_scale):
    """Thực hiện phân tích mức độ lỗi (ELA) trên hình ảnh."""
    temp_path = "temp_ela.jpg"
    
    # Nén ảnh bằng chất lượng JPEG
    image.save(temp_path, "JPEG", quality=jpeg_quality)
    compressed_image = Image.open(temp_path)
    
    # Tính sai lệch giữa ảnh gốc và ảnh đã nén
    ela_image = ImageChops.difference(image, compressed_image)
    
    # Tăng cường độ sáng của ảnh ELA
    enhancer = ImageEnhance.Brightness(ela_image)
    ela_image = enhancer.enhance(error_scale / 10.0)
    
    return ela_image
