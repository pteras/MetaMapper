import os
from tkinter import Tk, Label, Button, Entry, StringVar, filedialog, Checkbutton, BooleanVar, Radiobutton, IntVar
from tkinter import messagebox
from PIL import Image
from PIL.ExifTags import TAGS
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from fpdf import FPDF

# Functions to extract EXIF data
def extract_exif(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    if exif_data:
        return {TAGS.get(tag): value for tag, value in exif_data.items()}
    return {}

def extract_metadata(video_path):
    parser = createParser(video_path)
    metadata = extractMetadata(parser)
    if metadata:
        return metadata.exportDictionary()
    return {}

def get_exif_data(directory, process_images, process_videos):
    exif_data = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if process_images and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            exif_data[filename] = extract_exif(file_path)
        elif process_videos and filename.lower().endswith(('.mp4', '.mov', '.avi')):
            exif_data[filename] = extract_metadata(file_path)
    return exif_data

# Functions to generate reports
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'EXIF Data Report', 0, 1, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

def create_pdf_report(exif_data, output_path):
    pdf = PDFReport()
    pdf.add_page()
    
    for filename, data in exif_data.items():
        pdf.chapter_title(filename)
        body = "\n".join(f"{key}: {value}" for key, value in data.items())
        pdf.chapter_body(body)
    
    pdf.output(output_path)

def create_text_report(exif_data, output_path):
    with open(output_path, 'w') as file:
        for filename, data in exif_data.items():
            file.write(f"{filename}\n")
            for key, value in data.items():
                file.write(f"  {key}: {value}\n")
            file.write("\n")

def generate_report():
    directory = folder_path.get()
    output_directory = output_folder_path.get() or "results"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        
    if not directory:
        messagebox.showerror("Error", "Please select a folder.")
        return

    process_images = images_var.get()
    process_videos = videos_var.get()
    output_format = output_format_var.get()
    
    if not process_images and not process_videos:
        messagebox.showerror("Error", "Please select at least one file type (images or videos).")
        return
    
    if output_format not in [1, 2]:
        messagebox.showerror("Error", "Please select an output format.")
        return

    exif_data = get_exif_data(directory, process_images, process_videos)
    
    if output_format == 1:
        output_path = os.path.join(output_directory, 'exif_report.pdf')
        create_pdf_report(exif_data, output_path)
    elif output_format == 2:
        output_path = os.path.join(output_directory, 'exif_report.txt')
        create_text_report(exif_data, output_path)
    
    messagebox.showinfo("Success", f"Report generated: {output_path}")

def select_folder():
    folder = filedialog.askdirectory()
    folder_path.set(folder)

def select_output_folder():
    folder = filedialog.askdirectory()
    output_folder_path.set(folder)

# Setting up the Tkinter window
root = Tk()
root.title("MetaMapper")

folder_path = StringVar()
output_folder_path = StringVar()
images_var = BooleanVar()
videos_var = BooleanVar()
output_format_var = IntVar()

Label(root, text="Select Folder:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
Entry(root, textvariable=folder_path, width=50).grid(row=0, column=1, padx=10, pady=10)
Button(root, text="Browse", command=select_folder).grid(row=0, column=2, padx=10, pady=10)

Label(root, text="Output Folder:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
Entry(root, textvariable=output_folder_path, width=50).grid(row=1, column=1, padx=10, pady=10)
Button(root, text="Browse", command=select_output_folder).grid(row=1, column=2, padx=10, pady=10)

Label(root, text="Select File Types:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
Checkbutton(root, text="Images", variable=images_var).grid(row=2, column=1, sticky="w")
Checkbutton(root, text="Videos", variable=videos_var).grid(row=2, column=1)

Label(root, text="Select Output Format:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
Radiobutton(root, text="PDF", variable=output_format_var, value=1).grid(row=3, column=1, sticky="w")
Radiobutton(root, text="Text", variable=output_format_var, value=2).grid(row=3, column=1)

Button(root, text="Generate Report", command=generate_report).grid(row=4, column=0, columnspan=3, pady=20)

root.mainloop()
