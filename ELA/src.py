import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageChops, ImageEnhance

def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return
    global original_image, ela_image, original_photo, ela_photo

    # Load the original image
    original_image = Image.open(file_path)
    ela_image = perform_ela(original_image, jpeg_quality_slider.get(), error_scale_slider.get())

    # Convert images to Tkinter-compatible format
    original_photo = ImageTk.PhotoImage(original_image.resize((400, 400)))  # Bigger main frame
    ela_photo = ImageTk.PhotoImage(ela_image.resize((400, 400)))

    # Update the displayed images
    original_label.config(image=original_photo)
    ela_label.config(image=ela_photo)

    # Show additional UI components
    jpeg_quality_label.pack(pady=5)
    jpeg_quality_slider.pack(pady=5)
    error_scale_label.pack(pady=5)
    error_scale_slider.pack(pady=5)
    choose_button.pack(pady=10)

    # Hide the add image button
    add_image_button.pack_forget()


def perform_ela(image, jpeg_quality, error_scale):
    temp_path = "temp_ela.jpg"
    image.save(temp_path, "JPEG", quality=jpeg_quality)
    compressed_image = Image.open(temp_path)
    ela_image = ImageChops.difference(image, compressed_image)

    # Enhance the ELA result based on error scale
    enhancer = ImageEnhance.Brightness(ela_image)
    ela_image = enhancer.enhance(error_scale / 10.0)
    return ela_image


def update_ela(*args):
    if original_image is not None:
        global ela_image, ela_photo
        ela_image = perform_ela(original_image, jpeg_quality_slider.get(), error_scale_slider.get())
        ela_photo = ImageTk.PhotoImage(ela_image.resize((400, 400)))
        ela_label.config(image=ela_photo)


root = tk.Tk()
root.title("Error Level Analysis Tool")

original_image = None
ela_image = None

add_image_button = tk.Button(root, text="+", font=("Arial", 50), fg="black", bg="lightgrey", width=20, height=10, command=open_image)
add_image_button.pack(pady=20)

frame = tk.Frame(root)
frame.pack(pady=10)

original_label = tk.Label(frame)
original_label.grid(row=0, column=0, padx=5)
ela_label = tk.Label(frame)
ela_label.grid(row=0, column=1, padx=5)

jpeg_quality_label = tk.Label(root, text="JPEG Quality")
jpeg_quality_slider = tk.Scale(
    root, from_=0, to=100, orient=tk.HORIZONTAL, command=update_ela, length=400  # Longer slider
)
jpeg_quality_slider.set(75)

error_scale_label = tk.Label(root, text="Error Scale")
error_scale_slider = tk.Scale(
    root, from_=0, to=100, orient=tk.HORIZONTAL, command=update_ela, length=400  # Longer slider
)
error_scale_slider.set(10)
choose_button = tk.Button(root, text="Choose Another Image", command=open_image)

root.mainloop()
