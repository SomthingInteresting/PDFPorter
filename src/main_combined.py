#!/usr/bin/env python3

import tkinter as tk
import os
from tkinter import filedialog, messagebox, simpledialog
from shutil import copy2
import PyPDF2
import json
from pdfminer.high_level import extract_text

# Your pdf_operations functions

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

            third_line = text.splitlines()[0] if len(text.splitlines()) >= 3 else f"payslip_{i}"

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

def main():
    root = tk.Tk()
    root.title("PDFPorter")

    # Create a drop-down list of payslips
    input_pdf = filedialog.askopenfilename(title="Select Payroll PDF", filetypes=[("PDF Files", "*.pdf")])
    payslips = split_pdf(input_pdf)

    payslip_var = tk.StringVar(root)
    payslip_var.set(payslips[0])
    dropdown = tk.OptionMenu(root, payslip_var, *payslips)
    dropdown.pack()

    # Frame to contain Listbox and Scrollbar
    folder_frame = tk.Frame(root)
    folder_frame.pack(fill=tk.BOTH, expand=1)

    # Horizontal Scrollbar for the Listbox
    h_scroll = tk.Scrollbar(folder_frame, orient=tk.HORIZONTAL)
    h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    # Listbox to show selected folders with associated scrollbar
    folders_listbox = tk.Listbox(folder_frame, xscrollcommand=h_scroll.set)
    folders_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    h_scroll.config(command=folders_listbox.xview)

    # Button to add folders
    button_add = tk.Button(root, text="Add Folder", command=lambda: copy_file_to_destinations(payslip_var.get(), folders_listbox))
    button_add.pack()

    # Button to remove selected folder
    def remove_selected_folder():
        if folders_listbox.curselection():
            folders_listbox.delete(folders_listbox.curselection()[0])

    button_remove = tk.Button(root, text="Remove Folder", command=remove_selected_folder)
    button_remove.pack()

    # Listbox to show saved groups
    groups_listbox = tk.Listbox(root)
    groups_listbox.pack()
    for group in load_folder_groups():
        groups_listbox.insert(tk.END, group)

    # Button to save current folder group
    def save_current_group():
        group_name = simpledialog.askstring("Input", "Enter name for the folder group:")
        if group_name:
            folders = folders_listbox.get(0, tk.END)
            save_folder_group(group_name, folders)
            groups_listbox.insert(tk.END, group_name)

    button_save_group = tk.Button(root, text="Save Group", command=save_current_group)
    button_save_group.pack()

    # Button to load selected group to main folder listbox
    def load_group():
        selected_group = groups_listbox.get(groups_listbox.curselection())
        if selected_group:
            folders = load_selected_group(selected_group)
            folders_listbox.delete(0, tk.END)  # Clear current list
            for folder in folders:
                folders_listbox.insert(tk.END, folder)

    button_load_group = tk.Button(root, text="Load Group", command=load_group)
    button_load_group.pack()

    # Button to remove selected group from saved groups listbox and json file
    def remove_group():
        selected_group = groups_listbox.get(groups_listbox.curselection())
        if selected_group:
            # Remove from the listbox
            groups_listbox.delete(groups_listbox.curselection())
            # Remove from the json file
            remove_folder_group(selected_group)
            messagebox.showinfo("Removed", f"Group '{selected_group}' has been removed.")

    button_remove_group = tk.Button(root, text="Remove Group", command=remove_group)
    button_remove_group.pack()

    # Button to perform the copy action
    def copy_selected_payslip_to_folders():
        payslip = payslip_var.get()
        print(f"Copying {payslip} to:")
        success = True
        for folder in folders_listbox.get(0, tk.END):
            dest = os.path.join(folder, os.path.basename(payslip))
            print(f" -> {dest}")
            try:
                copy2(payslip, dest)
            except Exception as e:
                print(f"Failed to copy to {dest}. Error: {e}")
                success = False
        if success:
            messagebox.showinfo("Success", f"Successfully copied {payslip} to selected folders.")
        else:
            messagebox.showerror("Error", f"Failed to copy {payslip} to one or more folders. Check the console for details.")

    button_copy = tk.Button(root, text="Copy to Selected Folders", command=copy_selected_payslip_to_folders)
    button_copy.pack()

    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)

    root.mainloop()

if __name__ == "__main__":
    main()
