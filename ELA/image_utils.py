from PIL import Image

def load_image(file_path):
    """Loads an image from the given file path and converts it based on the current mode."""
    try:
        image = Image.open(file_path)
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None
