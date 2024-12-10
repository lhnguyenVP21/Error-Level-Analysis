import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk
from image_loader import load_image
from jpeg_compression import perform_ela

# Initialize global variables
original_image = None
ela_image = None

def open_image():
    global original_image, ela_image, original_photo, ela_photo
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return

    # Load the original image
    original_image = load_image(file_path)
    ela_image = perform_ela(original_image, jpeg_quality_slider.get(), error_scale_slider.get())

    # Convert images to Tkinter-compatible format
    original_photo = ImageTk.PhotoImage(original_image.resize((400, 400)))
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


def update_ela(*args):
    if original_image is not None:
        global ela_image, ela_photo
        ela_image = perform_ela(original_image, jpeg_quality_slider.get(), error_scale_slider.get())
        ela_photo = ImageTk.PhotoImage(ela_image.resize((400, 400)))
        ela_label.config(image=ela_photo)


# Set up the main Tkinter window
root = tk.Tk()
root.title("Error Level Analysis Tool")

add_image_button = tk.Button(root, text="+", font=("Arial", 50), fg="black", bg="lightgrey", width=20, height=10, command=open_image)
add_image_button.pack(pady=20)

frame = tk.Frame(root)
frame.pack(pady=10)

original_label = tk.Label(frame)
original_label.grid(row=0, column=0, padx=5)
ela_label = tk.Label(frame)
ela_label.grid(row=0, column=1, padx=5)

jpeg_quality_label = tk.Label(root, text="JPEG Quality")
jpeg_quality_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=update_ela, length=400)
jpeg_quality_slider.set(75)

error_scale_label = tk.Label(root, text="Error Scale")
error_scale_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=update_ela, length=400)
error_scale_slider.set(10)

choose_button = tk.Button(root, text="Choose Another Image", command=open_image)

root.mainloop()
