import os
import tkinter as tk
from tkinter import filedialog, messagebox
import requests

SERVER_URL = "http://localhost:5000"


def _upload_image(path: str, output: tk.Text) -> None:
    """Upload a single image and show the result in the text widget."""
    with open(path, "rb") as f:
        files = {"file": f}
        resp = requests.post(f"{SERVER_URL}/upload_image", files=files)

    name = os.path.basename(path)
    if resp.status_code != 200:
        output.insert(tk.END, f"Failed to upload {name}: {resp.text}\n\n")
        output.see(tk.END)
        return

    data = resp.json()
    image_id = data.get("image_id")
    caption = data.get("caption", "")
    tags = ", ".join(data.get("tags", []))

    persons_resp = requests.get(f"{SERVER_URL}/identify/{image_id}")
    persons = []
    if persons_resp.status_code == 200:
        for p in persons_resp.json().get("persons", []):
            persons.append(f"{p['person_id']} ({p['confidence']:.2f})")

    output.insert(
        tk.END,
        f"{name}\nCaption: {caption}\nTags: {tags}\nPersons: {', '.join(persons) or 'None'}\n\n",
    )
    output.see(tk.END)


def upload_folder(folder: str, output: tk.Text) -> None:
    """Upload all images from the folder to the picscreenr server."""
    for name in os.listdir(folder):
        if not name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            continue
        path = os.path.join(folder, name)
        _upload_image(path, output)


def choose_folder(output: tk.Text) -> None:
    folder = filedialog.askdirectory()
    if folder:
        upload_folder(folder, output)
        messagebox.showinfo("Upload", "Finished uploading images")


def choose_file(output: tk.Text) -> None:
    path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )
    if path:
        _upload_image(path, output)


root = tk.Tk()
root.title("Picscreenr Uploader")

text = tk.Text(root, width=60, height=20)
text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

tk.Button(button_frame, text="Upload Image", command=lambda: choose_file(text)).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Upload Folder", command=lambda: choose_folder(text)).pack(side=tk.LEFT, padx=5)

root.mainloop()
