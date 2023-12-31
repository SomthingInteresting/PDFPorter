import PyPDF2
import json
import os
import tkinter as tk
from shutil import copy2
from tkinter import filedialog
from pdfminer.high_level import extract_text

def split_pdf(input_pdf):
    with open(input_pdf, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(reader.pages)
        
        if num_pages == 0:
            return []

        payslips = []

        for i in range(num_pages):
            text = extract_text_from_pdf_page(input_pdf, i)
            
            # Skip processing if the page is blank
            if not text.strip():
                continue

            writer = PyPDF2.PdfWriter()
            writer.add_page(reader.pages[i])

            third_line = text.splitlines()[2] if len(text.splitlines()) >= 3 else f"payslip_{i}"

            # Replacing invalid characters for filenames
            for ch in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
                third_line = third_line.replace(ch, "_")

            output_pdf = f"{third_line}.pdf"  
            with open(output_pdf, "wb") as output_file:
                writer.write(output_file)

            payslips.append(output_pdf)

    return payslips

def extract_text_from_pdf_page(pdf_path, page_num):
    return extract_text(pdf_path, page_numbers=[page_num])

def copy_file_to_destinations(payslip, folders_listbox):
    folder = filedialog.askdirectory(title="Select Folder")
    if folder:
        print(f"Selected folder: {folder}")
        folders_listbox.insert(tk.END, folder)

FOLDER_GROUPS_FILE = "folder_groups.json"

def save_folder_group(group_name, folders):
    data = {}
    if os.path.exists(FOLDER_GROUPS_FILE):
        with open(FOLDER_GROUPS_FILE, "r") as f:
            data = json.load(f)
    data[group_name] = folders
    with open(FOLDER_GROUPS_FILE, "w") as f:
        json.dump(data, f)

def load_folder_groups():
    if os.path.exists(FOLDER_GROUPS_FILE):
        with open(FOLDER_GROUPS_FILE, "r") as f:
            data = json.load(f)
        return list(data.keys())
    return []

def load_selected_group(group_name):
    if os.path.exists(FOLDER_GROUPS_FILE):
        with open(FOLDER_GROUPS_FILE, "r") as f:
            data = json.load(f)
        return data.get(group_name, [])
    return []

def remove_folder_group(group_name):
    if os.path.exists(FOLDER_GROUPS_FILE):
        with open(FOLDER_GROUPS_FILE, "r") as f:
            data = json.load(f)
        if group_name in data:
            del data[group_name]
            with open(FOLDER_GROUPS_FILE, "w") as f:
                json.dump(data, f)
