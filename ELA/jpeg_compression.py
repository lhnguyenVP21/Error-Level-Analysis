from PIL import Image, ImageChops, ImageEnhance

def perform_ela(image, jpeg_quality, error_scale):
    """Perform Error Level Analysis (ELA) on the given image."""
    temp_path = "temp_ela.jpg"
    image.save(temp_path, "JPEG", quality=jpeg_quality)
    compressed_image = Image.open(temp_path)
    ela_image = ImageChops.difference(image, compressed_image)

    # Enhance the ELA result based on error scale
    enhancer = ImageEnhance.Brightness(ela_image)
    ela_image = enhancer.enhance(error_scale / 10.0)
    return ela_image
