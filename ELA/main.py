import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import ImageTk, ImageChops, ImageEnhance, Image
import os
import numpy as np
from image_utils import load_image, format_exif_info
from jpeg_compression import perform_ela, resize_image_to_block_size, compute_dct_jpeg_compression, cleanup_temp_files

original_rgb_image = None  
current_image = None 
ela_image = None
original_photo = None
ela_photo = None
current_mode = "RGB" 
current_file_path = None

def open_image():
    """Function to open and display the original image, ELA image, and EXIF information."""
    global original_rgb_image, current_image, ela_image, original_photo, ela_photo, current_file_path
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return

    current_file_path = file_path
    original_rgb_image = load_image(file_path)
    if original_rgb_image is None:
        return

    original_rgb_image = resize_image_to_block_size(original_rgb_image, 8)
    
    current_image = original_rgb_image.copy()
    
    ela_image = perform_ela(current_image, jpeg_quality_slider.get(), error_scale_slider.get())

    if ela_image is None:
        return

    display_images()
    display_exif_info()

def select_mode(mode):
    """Switches the current mode (RGB or L) and updates the current image display."""
    global current_mode, current_image, ela_image, original_photo, ela_photo

    if original_rgb_image is None:
        messagebox.showwarning("No Image", "Please select an image first.")
        return

    current_mode = mode
    print(f"Switching mode to {current_mode}")

    if current_mode == "L":
        current_image = original_rgb_image.convert('L')
    elif current_mode == "RGB":
        current_image = original_rgb_image.copy()

    ela_image = perform_ela(current_image, jpeg_quality_slider.get(), error_scale_slider.get())

    display_images()

def display_exif_info():
    """Display EXIF information in the text widget."""
    if current_file_path:
        exif_text.config(state=tk.NORMAL)
        exif_text.delete('1.0', tk.END)
        exif_info = format_exif_info(current_file_path)
        exif_text.insert(tk.END, exif_info)
        exif_text.config(state=tk.DISABLED)

def display_images():
    """Displays the current and ELA images."""
    global current_image, ela_image, original_photo, ela_photo

    if current_image is None or ela_image is None:
        return

    original_photo = ImageTk.PhotoImage(current_image.resize((400, 400)))
    ela_photo = ImageTk.PhotoImage(ela_image.resize((400, 400)))
    original_label.config(image=original_photo)
    ela_label.config(image=ela_photo)
    jpeg_quality_label.pack(pady=5)
    jpeg_quality_slider.pack(pady=5)
    error_scale_label.pack(pady=5)
    error_scale_slider.pack(pady=5)
    choose_button.pack(pady=10)
    
    exif_frame.pack(pady=10)

    add_image_button.pack_forget()

def update_ela(*args):
    """Updates the ELA image when slider values change."""
    if current_image is not None:
        global ela_image, ela_photo
        ela_image = perform_ela(current_image, jpeg_quality_slider.get(), error_scale_slider.get())
        if ela_image is None:
            return
        ela_photo = ImageTk.PhotoImage(ela_image.resize((400, 400)))
        ela_label.config(image=ela_photo)

root = tk.Tk()
root.title("Image Analysis Tool: ELA and EXIF")
root.geometry("1000x1200")  # Increased window size to accommodate EXIF info

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

# Placeholders for image labels (current and ELA images)
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

# Frame for EXIF information
exif_frame = tk.Frame(root)
exif_title = tk.Label(exif_frame, text="EXIF Information", font=("Arial", 12, "bold"))
exif_title.pack()

# Scrolled text widget to display EXIF information
exif_text = scrolledtext.ScrolledText(exif_frame, wrap=tk.WORD, width=60, height=10, state=tk.DISABLED)
exif_text.pack(padx=10, pady=10)

# Start the Tkinter main loop
root.protocol("WM_DELETE_WINDOW", lambda: (cleanup_temp_files(), root.destroy()))  # Cleanup temp files on exit
root.mainloop()