import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import os


def load_dct_tables():
    """Loads the quantization matrix, DC codes, and AC codes from files."""
    try:
        Q = np.loadtxt('dct/Quantization_Matrix.txt', delimiter='\t', dtype=int)
        DC_Codes = np.loadtxt('dct/JPEG_DC_Codes.txt', delimiter='\t', dtype=str)
        AC_Codes = np.loadtxt('dct/JPEG_AC_Codes.txt', delimiter='\t', dtype=str)
        return Q, DC_Codes, AC_Codes
    except Exception as e:
        print(f"Error loading DCT tables: {e}")
        return None, None, None


def compute_forward_2d_dct(block):
    """Computes the 2D Discrete Cosine Transform (DCT) for an 8x8 block."""
    N = block.shape[0]
    dct_block = np.zeros_like(block, dtype=float)
    c = lambda x: 1 / np.sqrt(2) if x == 0 else 1
    
    for u in range(N):
        for v in range(N):
            sum_ = sum(
                block[x, y] * np.cos((2 * x + 1) * u * np.pi / (2 * N)) * np.cos((2 * y + 1) * v * np.pi / (2 * N))
                for x in range(N) for y in range(N)
            )
            dct_block[u, v] = 0.25 * c(u) * c(v) * sum_
    
    return dct_block


def quantize_dct_image(dct_block, Q):
    """Quantizes the DCT image using the quantization matrix Q."""
    return np.round(dct_block / Q)


def construct_zigzag_array(matrix):
    """Constructs a flattened array from a given matrix using a zigzag pattern."""
    N = matrix.shape[0]
    result = []
    for i in range(2 * N - 1):
        if i % 2 == 0:
            result.extend(matrix[diag, i - diag] for diag in range(max(0, i - N + 1), min(i + 1, N)))
        else:
            result.extend(matrix[i - diag, diag] for diag in range(max(0, i - N + 1), min(i + 1, N)))
    return np.array(result)


def compute_dct_jpeg_compression(image):
    """Computes JPEG compression on an image using DCT and quantization."""
    Q, DC_Codes, AC_Codes = load_dct_tables()
    if Q is None or DC_Codes is None or AC_Codes is None:
        print("Error: Could not load DCT-related files.")
        return None
    
    N = image.shape[0]
    block_size = Q.shape[0]
    compressed_data = ''
    previous_dc = 0  # Initial DC coefficient is assumed to be 0
    
    for i in range(0, N, block_size):
        for j in range(0, N, block_size):
            block = image[i:i + block_size, j:j + block_size]
            block_dct = compute_forward_2d_dct(block)
            block_quantized = quantize_dct_image(block_dct, Q)
            block_zigzag = construct_zigzag_array(block_quantized)
            
            dc = block_zigzag[0] if block_zigzag.size > 0 else 0
            dc_diff = dc - previous_dc
            previous_dc = dc
            
            bin_dc = bin(abs(dc_diff))[2:]
            if dc_diff < 0:
                bin_dc = ''.join('1' if bit == '0' else '0' for bit in bin_dc)
            
            dc_index = next((i for i, code in enumerate(DC_Codes) if code[0] == str(len(bin_dc))), None)
            if dc_index is not None:
                compressed_data += DC_Codes[dc_index][1] + bin_dc
            
            ac_run_length = 0
            for ac in block_zigzag[1:]:
                if ac == 0:
                    ac_run_length += 1
                else:
                    ac_size = len(bin(abs(ac))[2:])
                    ac_code = f'{ac_run_length}/{ac_size}'
                    ac_index = next((i for i, code in enumerate(AC_Codes) if code[0] == ac_code), None)
                    if ac_index is not None:
                        compressed_data += AC_Codes[ac_index][1] + bin(abs(ac))[2:]
                    ac_run_length = 0
            compressed_data += AC_Codes[0][1]  # EOB
    
    return compressed_data

def load_image(file_path):
    """Loads an image from the given file path and converts it to grayscale."""
    try:
        image = Image.open(file_path).convert('RGB')  # Keep the image in RGB format
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def resize_image_to_block_size(image, block_size):
    """Resizes the image so that its dimensions are multiples of the block size."""
    width, height = image.size
    new_width = (width // block_size) * block_size
    new_height = (height // block_size) * block_size
    return image.resize((new_width, new_height))

def perform_ela(image, jpeg_quality, error_scale):
    """Performs Error Level Analysis (ELA) on the image."""
    try:
        temp_path = 'output/temp_ela.jpg'
        image.save(temp_path, 'JPEG', quality=jpeg_quality)
        compressed_image = Image.open(temp_path).convert('RGB')
        ela_image = ImageChops.difference(image, compressed_image)
        ela_image = ImageEnhance.Brightness(ela_image).enhance(error_scale / 10.0)
        return ela_image
    except Exception as e:
        print(f"Error performing ELA: {e}")
        return None

def save_temp_image(image, jpeg_quality):
    """Saves a temporary image file as a compressed JPEG."""
    temp_path = 'output/temp_ela.jpg'
    try:
        image.save(temp_path, 'JPEG', quality=jpeg_quality)
    except Exception as e:
        print(f"Error saving temp image: {e}")
    return temp_path


def cleanup_temp_files():
    """Removes temporary files used in the process."""
    temp_path = 'output/temp_ela.jpg'
    if os.path.exists(temp_path):
        os.remove(temp_path)
