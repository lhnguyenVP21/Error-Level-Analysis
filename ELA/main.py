import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, ImageChops, ImageEnhance, Image
import os
import numpy as np
from image_utils import load_image  # Import load_image from image_utils.py
from jpeg_compression import perform_ela, resize_image_to_block_size, compute_dct_jpeg_compression,cleanup_temp_files
# Khai báo các biến toàn cục để lưu trạng thái của ảnh
original_image = None
ela_image = None
original_photo = None
ela_photo = None
current_mode = "L"  # Default mode is grayscale (L)

def open_image():
    """Function to open and display the original image and ELA image."""
    global original_image, ela_image, original_photo, ela_photo
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return

    original_image = load_image(file_path)  # Now using the load_image function from image_utils
    if original_image is None:
        return

    # Resize image to be multiple of 8x8 (for DCT compression compatibility)
    original_image = resize_image_to_block_size(original_image, 8)
    ela_image = perform_ela(original_image, jpeg_quality_slider.get(), error_scale_slider.get())

    if ela_image is None:
        return

    # Convert images to Tkinter-compatible format
    display_images()

def select_mode(mode):
    """Switches the current mode (RGB or L) and updates the current image display."""
    global current_mode, original_image, ela_image, original_photo, ela_photo

    # Kiểm tra nếu chưa có ảnh được tải lên
    if original_image is None:
        messagebox.showwarning("Chưa có ảnh", "Vui lòng chọn ảnh trước khi thay đổi chế độ.")
        return  # Dừng lại nếu chưa có ảnh

    current_mode = mode
    print(f"Switching mode to {current_mode}")
    print(f"Original image mode: {original_image.mode}")
    print(f"ELA image mode: {ela_image.mode}")


    # Convert the current image to the selected mode (RGB or L)
    original_image = convert_image_mode(original_image)

    # Perform ELA again on the new mode image
    ela_image = perform_ela(original_image, jpeg_quality_slider.get(), error_scale_slider.get())

    # Display the images after mode change
    display_images()

def convert_image_mode(image):
    """Converts the image to the current mode (RGB or L)."""
    if current_mode == "L":
        return image.convert('L')  # Convert to grayscale
    elif current_mode == "RGB":
        return image.convert('RGB')  # Convert to RGB
    return image


def display_images():
    """Displays the original and ELA images."""
    global original_image, ela_image, original_photo, ela_photo

    if original_image is None or ela_image is None:
        return

    # Chuyển đổi ảnh thành định dạng tương thích với Tkinter
    original_photo = ImageTk.PhotoImage(original_image.resize((400, 400)))
    ela_photo = ImageTk.PhotoImage(ela_image.resize((400, 400)))

    # Cập nhật ảnh hiển thị
    original_label.config(image=original_photo)
    ela_label.config(image=ela_photo)

    # Hiển thị các slider và nút sau khi ảnh đã được tải
    jpeg_quality_label.pack(pady=5)
    jpeg_quality_slider.pack(pady=5)
    error_scale_label.pack(pady=5)
    error_scale_slider.pack(pady=5)
    choose_button.pack(pady=10)

    # Ẩn nút "+" khi ảnh đã được tải
    add_image_button.pack_forget()

def update_ela(*args):
    """Updates the ELA image when slider values change."""
    if original_image is not None:
        global ela_image, ela_photo
        ela_image = perform_ela(original_image, jpeg_quality_slider.get(), error_scale_slider.get())
        if ela_image is None:
            return
        ela_photo = ImageTk.PhotoImage(ela_image.resize((400, 400)))
        ela_label.config(image=ela_photo)

# Set up the main Tkinter window
root = tk.Tk()
root.title("Error Level Analysis Tool")

# Buttons to toggle RGB and L mode
rgb_button = tk.Button(root, text="RGB", width=10, command=lambda: select_mode("RGB"))
rgb_button.pack(side=tk.LEFT, padx=10, pady=10)

l_button = tk.Button(root, text="L (Grayscale)", width=10, command=lambda: select_mode("L"))
l_button.pack(side=tk.LEFT, padx=10, pady=10)

# Add button to upload the image
add_image_button = tk.Button(root, text="+", font=("Arial", 50), fg="black", bg="lightgrey", width=20, height=10, command=open_image)
add_image_button.pack(pady=20)

# Create a frame to hold the image previews
frame = tk.Frame(root)
frame.pack(pady=10)

# Placeholders for image labels (original and ELA images)
original_label = tk.Label(frame)
original_label.grid(row=0, column=0, padx=5)
ela_label = tk.Label(frame)
ela_label.grid(row=0, column=1, padx=5)

# Labels and sliders for JPEG quality and error scale
jpeg_quality_label = tk.Label(root, text="JPEG Quality")
jpeg_quality_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=update_ela, length=400)
jpeg_quality_slider.set(75)  # Default JPEG quality

error_scale_label = tk.Label(root, text="Error Scale")
error_scale_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=update_ela, length=400)
error_scale_slider.set(10)  # Default error scale

# Button to choose another image
choose_button = tk.Button(root, text="Choose Another Image", command=open_image)

# Start the Tkinter main loop
root.protocol("WM_DELETE_WINDOW", lambda: (cleanup_temp_files(), root.destroy()))  # Cleanup temp files on exit
root.mainloop()
