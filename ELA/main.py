import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import ImageTk, Image
from image_utils import load_image, format_exif_info
from jpeg_compression import perform_ela, resize_image_to_block_size, cleanup_temp_files

original_rgb_image = None
current_image = None
ela_image = None
original_photo = None
ela_photo = None
current_mode = "RGB" 
current_file_path = None
exif_visible = False

def open_image():
    """Function to open and display the original image, ELA image, and EXIF information."""
    global original_rgb_image, current_image, ela_image, original_photo, ela_photo, current_file_path
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return

    current_file_path = file_path
    original_rgb_image = load_image(file_path)
    if original_rgb_image is None:
        messagebox.showerror("Error", "Failed to load the image.")
        return

    original_rgb_image = resize_image_to_block_size(original_rgb_image, 8)
    current_image = original_rgb_image.copy()
    update_ela()

    if ela_image is None:
        messagebox.showerror("Error", "ELA computation failed.")
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
    current_image = original_rgb_image.convert('L') if mode == "L" else original_rgb_image.copy()
    update_ela()
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

    add_image_button.pack_forget()
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

def update_ela(*args):
    """Updates the ELA image when slider values change."""
    if current_image is not None:
        global ela_image, ela_photo
        ela_image = perform_ela(current_image, jpeg_quality_slider.get(), error_scale_slider.get())
        if ela_image is None:
            return
        ela_photo = ImageTk.PhotoImage(ela_image.resize((400, 400)))
        ela_label.config(image=ela_photo)
def toggle_exif_visibility():
    global exif_visible
    exif_visible = not exif_visible
    if exif_visible:
        exif_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        display_exif_info()  # Load EXIF information when the frame is shown
        toggle_exif_button.config(text="Hide EXIF")
    else:
        exif_frame.pack_forget()
        toggle_exif_button.config(text="Show EXIF")
# Tkinter window setup
root = tk.Tk()
root.title("Image Analysis Tool: ELA and EXIF")
root.geometry("1400x800")
root.config(bg="white")

# Add button to upload the image
add_image_button = tk.Button(root, text="+", font=("Arial", 50), fg="black", bg="lightgrey", command=open_image)
add_image_button.pack(pady=50)

# Left Panel: Controls
left_frame = tk.Frame(root, bg="white", width=300, padx=10, pady=10)

# Frame for RGB and Grayscale buttons
mode_frame = tk.Frame(left_frame, bg="white")
mode_frame.pack(pady=5)

rgb_button = tk.Button(mode_frame, text="RGB", command=lambda: select_mode("RGB"), width=10)
rgb_button.pack(side=tk.LEFT, padx=5)

l_button = tk.Button(mode_frame, text="Grayscale (L)", command=lambda: select_mode("L"), width=10)
l_button.pack(side=tk.LEFT, padx=5)


jpeg_quality_label = tk.Label(left_frame, text="JPEG Quality", font=("Arial", 10), bg="white")
jpeg_quality_label.pack(pady=(20,5))
jpeg_quality_slider = tk.Scale(left_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=update_ela, length=400)
jpeg_quality_slider.set(75)
jpeg_quality_slider.pack()

error_scale_label = tk.Label(left_frame, text="Error Scale", font=("Arial", 10), bg="white")
error_scale_label.pack(pady=(20,5))
error_scale_slider = tk.Scale(left_frame, from_=1, to=50, orient=tk.HORIZONTAL, command=update_ela, length=400)
error_scale_slider.set(10)
error_scale_slider.pack()

choose_button = tk.Button(left_frame, text="Choose Another Image", command=open_image)
choose_button.pack(pady=10)

# Right Panel: Images and EXIF
right_frame = tk.Frame(root, bg="white", padx=10, pady=10)

# Image Previews
image_frame = tk.Frame(right_frame, bg='white')
image_frame.pack(pady=10)

original_label = tk.Label(image_frame)
original_label.pack(side=tk.LEFT, padx=10)
ela_label = tk.Label(image_frame)
ela_label.pack(side=tk.RIGHT, padx=10)

# Add a button to toggle EXIF information visibility
toggle_exif_button = tk.Button(right_frame, text="Show EXIF", command=toggle_exif_visibility, width=20)
toggle_exif_button.pack(pady=10)
# Frame for EXIF information
exif_frame = tk.LabelFrame(right_frame, text="EXIF Information", bg="white", padx=10, pady=10, width=400)
# exif_frame.pack(fill=tk.BOTH, expand=True,pady=20)

exif_text = scrolledtext.ScrolledText(exif_frame, wrap=tk.WORD, width=30, height=10, state=tk.DISABLED)
exif_text.pack(fill=tk.BOTH, expand=True)




# Cleanup on close
root.protocol("WM_DELETE_WINDOW", lambda: (cleanup_temp_files(), root.destroy()))

# Start Tkinter main loop
root.mainloop()
