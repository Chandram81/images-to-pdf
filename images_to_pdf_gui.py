import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageOps
import os

# Optional HEIC/HEIF support.
# Install with: pip install pillow-heif
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False


class ImagesToPDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Images → PDF")
        self.root.geometry("900x620")
        self.root.minsize(760, 520)

        self.files = []

        self.build_ui()

    def build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        header = ttk.Frame(self.root, padding=(20, 18, 20, 10))
        header.pack(fill="x")

        ttk.Label(
            header,
            text="Images → PDF",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Add images, arrange them, and export them as a single PDF.",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        toolbar = ttk.Frame(self.root, padding=(20, 8))
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="Add Images", command=self.add_images).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(toolbar, text="Remove Selected", command=self.remove_selected).pack(
            side="left", padx=8
        )
        ttk.Button(toolbar, text="Clear All", command=self.clear_all).pack(
            side="left", padx=8
        )

        ttk.Separator(toolbar, orient="vertical").pack(
            side="left", fill="y", padx=12
        )

        ttk.Button(toolbar, text="↑ Move Up", command=self.move_up).pack(
            side="left", padx=4
        )
        ttk.Button(toolbar, text="↓ Move Down", command=self.move_down).pack(
            side="left", padx=4
        )

        list_frame = ttk.LabelFrame(
            self.root, text="Images (PDF page order)", padding=10
        )
        list_frame.pack(fill="both", expand=True, padx=20, pady=(4, 10))

        self.listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            font=("Segoe UI", 10),
            activestyle="none"
        )
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.listbox.yview
        )
        self.listbox.configure(yscrollcommand=scrollbar.set)

        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        bottom = ttk.Frame(self.root, padding=(20, 5, 20, 15))
        bottom.pack(fill="x")

        self.status_var = tk.StringVar(value="No images added.")
        ttk.Label(
            bottom,
            textvariable=self.status_var,
            font=("Segoe UI", 9)
        ).pack(side="left")

        ttk.Button(
            bottom,
            text="Create PDF",
            command=self.create_pdf
        ).pack(side="right")

        self.root.bind("<Delete>", lambda event: self.remove_selected())
        self.root.bind("<Control-o>", lambda event: self.add_images())
        self.root.bind("<Control-s>", lambda event: self.create_pdf())

    def add_images(self):
        paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff *.heic *.heif"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("WebP", "*.webp"),
                ("Bitmap", "*.bmp"),
                ("TIFF", "*.tif *.tiff"),
                ("HEIC / HEIF", "*.heic *.heif"),
                ("All files", "*.*")
            ]
        )

        if not paths:
            return

        existing = set(self.files)
        added = 0

        for path in paths:
            path = os.path.abspath(path)
            if path not in existing:
                self.files.append(path)
                existing.add(path)
                added += 1

        self.refresh_list()

        if added:
            self.status_var.set(
                f"{len(self.files)} image(s) ready. {added} added."
            )

    def refresh_list(self):
        self.listbox.delete(0, tk.END)

        for index, path in enumerate(self.files, start=1):
            name = os.path.basename(path)
            self.listbox.insert(tk.END, f"{index:03d}  •  {name}")

        if self.files:
            self.status_var.set(f"{len(self.files)} image(s) ready.")
        else:
            self.status_var.set("No images added.")

    def remove_selected(self):
        selected = list(self.listbox.curselection())

        if not selected:
            messagebox.showinfo("Remove", "Select one or more images first.")
            return

        for index in reversed(selected):
            del self.files[index]

        self.refresh_list()

    def clear_all(self):
        if not self.files:
            return

        if messagebox.askyesno(
            "Clear All",
            "Remove all images from the list?"
        ):
            self.files.clear()
            self.refresh_list()

    def move_up(self):
        selected = list(self.listbox.curselection())

        if not selected:
            return

        # Preserve relative order while moving the selected block upward.
        for index in selected:
            if index > 0 and (index - 1) not in selected:
                self.files[index - 1], self.files[index] = (
                    self.files[index],
                    self.files[index - 1],
                )

        self.refresh_list()

        new_selection = [max(0, i - 1) for i in selected]
        for index in new_selection:
            self.listbox.selection_set(index)

    def move_down(self):
        selected = list(self.listbox.curselection())

        if not selected:
            return

        # Move from bottom to top so indexes remain valid.
        for index in reversed(selected):
            if index < len(self.files) - 1 and (index + 1) not in selected:
                self.files[index + 1], self.files[index] = (
                    self.files[index],
                    self.files[index + 1],
                )

        self.refresh_list()

        new_selection = [
            min(len(self.files) - 1, i + 1) for i in selected
        ]
        for index in new_selection:
            self.listbox.selection_set(index)

    def create_pdf(self):
        if not self.files:
            messagebox.showwarning(
                "No Images",
                "Add at least one image before creating the PDF."
            )
            return

        output = filedialog.asksaveasfilename(
            title="Save PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="images.pdf"
        )

        if not output:
            return

        images = []

        try:
            self.status_var.set("Preparing images...")
            self.root.update_idletasks()

            for path in self.files:
                if os.path.splitext(path)[1].lower() in (".heic", ".heif") and not HEIC_SUPPORTED:
                    raise RuntimeError(
                        "HEIC/HEIF images require the 'pillow-heif' package. "
                        "Run: pip install Pillow pillow-heif"
                    )

                with Image.open(path) as source:
                    # Apply EXIF orientation before converting to RGB.
                    image = ImageOps.exif_transpose(source)

                    # PDF requires RGB/RGBA/CMYK-compatible data.
                    if image.mode in ("RGBA", "LA"):
                        background = Image.new("RGB", image.size, "white")
                        alpha = image.getchannel("A")
                        background.paste(image.convert("RGB"), mask=alpha)
                        image = background
                    elif image.mode not in ("RGB", "L", "CMYK"):
                        image = image.convert("RGB")
                    elif image.mode == "L":
                        image = image.convert("RGB")

                    images.append(image.copy())

            self.status_var.set("Creating PDF...")
            self.root.update_idletasks()

            first = images[0]
            remaining = images[1:]

            first.save(
                output,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=remaining
            )

            for image in images:
                image.close()

            self.status_var.set(
                f"PDF created successfully: {os.path.basename(output)}"
            )

            if messagebox.askyesno(
                "PDF Created",
                f"PDF created successfully.\n\n{output}\n\n"
                "Open the output folder?"
            ):
                self.open_folder(output)

        except Exception as exc:
            for image in images:
                try:
                    image.close()
                except Exception:
                    pass

            messagebox.showerror(
                "Conversion Error",
                f"Could not create the PDF.\n\n{exc}"
            )
            self.status_var.set("PDF creation failed.")

    @staticmethod
    def open_folder(file_path):
        folder = os.path.dirname(os.path.abspath(file_path))

        if os.name == "nt":
            os.startfile(folder)
        elif os.name == "posix":
            import subprocess
            subprocess.Popen(["xdg-open", folder])


def main():
    root = tk.Tk()
    ImagesToPDFApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
