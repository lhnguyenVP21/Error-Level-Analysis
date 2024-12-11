import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk
import os
import numpy as np
from jpeg_compression import load_image, resize_image_to_block_size, perform_ela  # Import functions from jpeg_compression

# Global variables to store image states
global original_image, ela_image, original_photo, ela_photo


def open_image():
    """Function to open and display the original image and ELA image."""
    global original_image, ela_image, original_photo, ela_photo
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return

    original_image = load_image(file_path)
    if original_image is None:
        return
    
    # Resize image to be multiple of 8x8 (for DCT compression compatibility)
    original_image = resize_image_to_block_size(original_image, 8)
    ela_image = perform_ela(original_image, jpeg_quality_slider.get(), error_scale_slider.get())

    if ela_image is None:
        return

    # Convert images to Tkinter-compatible format
    original_photo = ImageTk.PhotoImage(original_image.resize((400, 400)))
    ela_photo = ImageTk.PhotoImage(ela_image.resize((400, 400)))

    # Update the displayed images
    original_label.config(image=original_photo)
    ela_label.config(image=ela_photo)

    # Show sliders and buttons after image is loaded
    jpeg_quality_label.pack(pady=5)
    jpeg_quality_slider.pack(pady=5)
    error_scale_label.pack(pady=5)
    error_scale_slider.pack(pady=5)
    choose_button.pack(pady=10)

    # Hide the "+" button
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


def cleanup_temp_files():
    """Remove temporary files used in the process."""
    temp_path = 'temp_ela.jpg'
    if os.path.exists(temp_path):
        os.remove(temp_path)


# Set up the main Tkinter window
root = tk.Tk()
root.title("Error Level Analysis Tool")

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