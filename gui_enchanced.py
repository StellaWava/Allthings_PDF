"""_summary_
    THIS IS AN ENHANCED VERSION OF GUI.py
    This script is applying Tkinter, a python graphical user interface to user-friendly GUI for 
    extracting text and table content from very old image scans. If it applies to old scans,
    it also applies to fresh images. 
    
    Note*** This particular script is suitable for small volumes of data. 
"""

"""_summary_

    Returns:
        _type_: _A left scroll is required to scroll through large documents
"""
#import libraries
import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Text
from PIL import Image, ImageTk
from pdf2image import convert_from_path
import pytesseract

#Create functions to -- input data, extract data, save data
# Function to open files --input data
def open_file():
    global all_text
    pdfpath = filedialog.askopenfilename(
        filetypes=[("Files", "*.tiff *.tif *.jpg *.png *.pdf")]
    )
    if pdfpath:
        all_text = extract_text(pdfpath)

#Function to extract  data
#store all pdf images loaded
pdf_images = []
current_page = 0

def extract_text(pdfpath):
    global pdf_images, current_page, all_text
    text = ""
    pdf_images = []  # Reset the images list
    current_page = 0  # Start at the first page

    try:
        if pdfpath.lower().endswith(('.tiff', '.tif', '.jpg', '.png')):
            img = Image.open(pdfpath)
            img = img.resize((595, 842))  # Resizing to A4
            show_image_window(img)
            text = pytesseract.image_to_string(img)  # extract text from the image
        elif pdfpath.lower().endswith('.pdf'):
            images = convert_from_path(pdfpath)  # Convert PDF to list of images
            pdf_images = [img.resize((595, 842)) for img in images]  # Store resized images
            show_image_window(pdf_images[current_page])  # Show the first page
            for page_num, img in enumerate(pdf_images):
                text += f"\n--- Page {page_num + 1} ---\n"
                text += pytesseract.image_to_string(img)
        else:
            messagebox.showerror("Error", "Unsupported file format!")
            return

        # Display the extracted text in the text area
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, text)
        status_label.config(text=f"Extracted text from {pdfpath}")

        return text
    except Exception as e:
        messagebox.showerror("Error", f"Failed to extract text: {str(e)}")
        return

# Function to navigate to the next page
def next_page():
    global current_page
    if current_page < len(pdf_images) - 1:
        current_page += 1
        show_image_window(pdf_images[current_page])

# Function to navigate to the previous page
def prev_page():
    global current_page
    if current_page > 0:
        current_page -= 1
        show_image_window(pdf_images[current_page])


# Function to save all extracted text to a file
def save_text():
    global all_text
    if not all_text:
        messagebox.showwarning("Save Error", "No text to save!")
        return

    outputfolder = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if outputfolder:
        with open(outputfolder, "w") as file:
            file.write(all_text)
        messagebox.showinfo("Save Success", f"Text saved to {outputfolder}")

#DISPLAY IMAGE WINDOW
# Function to show the image  
def show_image_window(img):
    # Clear any previous image on the canvas
    canvas.delete("all")

    # Convert image for display in Tkinter
    tk_img = ImageTk.PhotoImage(img)
    canvas.img = tk_img  # Keep a reference to avoid garbage collection

    # Update canvas size and display the image (without horizontal scroll)
    canvas.config(scrollregion=(0, 0, tk_img.width(), tk_img.height()))
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

    # Store the start and end coordinates of the rectangle
    rect = None
    start_x = start_y = end_x = end_y = 0

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red') #change color to prefered

    def on_mouse_move(event):
        nonlocal rect, end_x, end_y
        end_x, end_y = event.x, event.y
        canvas.coords(rect, start_x, start_y, end_x, end_y)

    def on_mouse_up(event):
        nonlocal end_x, end_y
        end_x, end_y = event.x, event.y

        # Ensure the coordinates are ordered correctly for cropping
        left = min(start_x, end_x)
        right = max(start_x, end_x)
        top = min(start_y, end_y)
        bottom = max(start_y, end_y)

        # Crop the selected area from the image and perform OCR
        crop_img = img.crop((left, top, right, bottom))
        text = pytesseract.image_to_string(crop_img)

        # Display the extracted text in the text area
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, text)
        status_label.config(text=f"Extracted text from selected area")

    # Bind mouse events to canvas for text selection
    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_move)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

# Initialize the Tkinter window
root = tk.Tk()
root.title("Image and PDF Text Extractor")

# Set window size to accommodate A4-sized page on the left frame
root.geometry('1200x900')  # Full window size

# Create two frames side by side with a small divider
left_frame = tk.Frame(root, width=595, height=842)  # A4 size in pixels: 595x842
left_frame.grid(row=0, column=0, padx=1, pady=10, sticky='nsew')

right_frame = tk.Frame(root, width=600, height=850)
right_frame.grid(row=0, column=1, padx=1, pady=10, sticky='nsew')

# Configure the grid to make the divider small
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Canvas and scrollbars for the image/PDF in the left frame (no horizontal scroll)
canvas = tk.Canvas(left_frame, width=595, height=842)  # Exact A4 dimensions
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Only the vertical scrollbar remains
y_scroll = Scrollbar(left_frame, orient=tk.VERTICAL, command=canvas.yview)
y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
canvas.config(yscrollcommand=y_scroll.set)

# Text area and scrollbar in the right frame
text_area = Text(right_frame, wrap=tk.WORD)
text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

text_scroll = Scrollbar(right_frame, command=text_area.yview)
text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
text_area.config(yscrollcommand=text_scroll.set)

# Buttons for opening and saving files in respective frames
open_button = tk.Button(left_frame, text="Open File", command=open_file)
open_button.pack(side=tk.TOP, padx=10, pady=10)

save_button = tk.Button(right_frame, text="Save Text", command=save_text)
save_button.pack(side=tk.TOP, padx=10, pady=10)

# Add Previous and Next buttons for navigation
prev_button = tk.Button(left_frame, text="Previous Page", command=prev_page)
prev_button.pack(side=tk.TOP, padx=10, pady=10)

next_button = tk.Button(left_frame, text="Next Page", command=next_page)
next_button.pack(side=tk.TOP, padx=10, pady=10)

# Status label at the bottom
status_label = tk.Label(root, text="No image loaded")
status_label.grid(row=1, column=0, columnspan=2, pady=5)

# Run the Tkinter main loop
root.mainloop()