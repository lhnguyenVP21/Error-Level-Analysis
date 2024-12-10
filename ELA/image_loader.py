from PIL import Image

def load_image(file_path):
    """Load an image from the given file path."""
    return Image.open(file_path)
