import os
import tkinter as tk
from tkinter import filedialog, messagebox
import requests

SERVER_URL = "http://localhost:5000"


def upload_images(folder: str):
    """Upload all images from the folder to the picscreenr server."""
    for name in os.listdir(folder):
        if not name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            continue
        path = os.path.join(folder, name)
        with open(path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{SERVER_URL}/upload_image", files=files)
            if response.status_code != 200:
                print(f"Failed to upload {name}: {response.text}")


def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        upload_images(folder)
        messagebox.showinfo("Upload", "Finished uploading images")


root = tk.Tk()
root.title("Picscreenr Uploader")
btn = tk.Button(root, text="Choose Image Folder", command=choose_folder)
btn.pack(padx=20, pady=20)
root.mainloop()
