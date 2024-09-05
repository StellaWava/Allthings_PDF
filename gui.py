"""_summary_
    This script is applying Tkinter, a python graphical user interface to user-friendly GUI for 
    extracting text and table content from very old image scans. If it applies to old scans,
    it also applies to fresh images. 
    
    Note*** This particular script is suitable for small volumes of data. 
"""
    
#import libraries
import os
import pdf2image
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import tkinter as tk
from tkinter import filedialog, Text, Scrollbar, messagebox

#experimenting with 1 file first.
pdfpath = r'file_path'
outputfolder = r'destination_path'
#read all files and subfoders from input folder
folder = os.walk(pdfpath)

for path, dir, file in folder:
    for y, f in enumerate(file):
        if f.endswith(',tiff'):
            filepath = os.path.join(path, f)
        print(y)

#function to open file
def open_file():
    global all_text
    pdfpath = filedialog.askopenfilename(
        filetypes=[("Files", "*.tiff *.tif *.jpg *.png")]
    )
    if pdfpath:
        all_text = extract_text(pdfpath)
#function for image extraction
def extract_text(pdfpath):
    img = Image.open(pdfpath)
    text = pytesseract.image_to_string(img)

    # Display extracted text in the Text widget for user review and correction
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, text)
    status_label.config(text=f"Extracted text from {os.path.basename(pdfpath)}")

# Function to save the corrected text to a file
def save_text():
    text = text_area.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Save Error", "No text to save!")
        return

    outputfolder = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if outputfolder:
        with open(outputfolder, "w") as file:
            file.write(text)
        messagebox.showinfo("Save Success", f"Text saved to {outputfolder}")
    
# Initialize the Tkinter window
root = tk.Tk()
root.title("Image Text Extractor")

# Create and place the widgets in the window
open_button = tk.Button(root, text="Open Image", command=open_file)
open_button.pack(pady=10)
status_label = tk.Label(root, text="No image loaded")
status_label.pack(pady=5)
text_frame = tk.Frame(root)
text_frame.pack(pady=5, fill=tk.BOTH, expand=True)
text_area = Text(text_frame, wrap=tk.WORD)
text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = Scrollbar(text_frame, command=text_area.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_area.config(yscrollcommand=scrollbar.set)

save_button = tk.Button(root, text="Save Text", command=save_text)

save_button.pack(pady=10)
#run the tool
root.mainloop()
