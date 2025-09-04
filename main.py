import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sv_ttk
import qrcode
from PIL import Image, ImageTk
import io
import os
import platform
import subprocess

class QRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Creator")
        sv_ttk.set_theme("dark")

        self.qr_images = []  # store (data_str, PIL_image, PhotoImage) tuples

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Enter text or URL:").pack(anchor='w')

        self.entry = ttk.Entry(frame, width=40)
        self.entry.pack(pady=10)

        self.generate_button = ttk.Button(frame, text="Generate QR Code", command=self.generate_qr)
        self.generate_button.pack(pady=10)

        self.qr_label = ttk.Label(frame)
        self.qr_label.pack(pady=20)

        # Buttons for save and share
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)

        self.save_button = ttk.Button(btn_frame, text="Save QR Code", command=self.save_qr, state='disabled')
        self.save_button.pack(side='left', padx=10)

        self.share_button = ttk.Button(btn_frame, text="Open/Share QR Code", command=self.share_qr, state='disabled')
        self.share_button.pack(side='left', padx=10)

        # Previous QR codes listbox
        ttk.Label(frame, text="Previous QR Codes:").pack(anchor='w', pady=(20,0))
        self.listbox = tk.Listbox(frame, height=5)
        self.listbox.pack(fill='x')
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

    def generate_qr(self):
        data = self.entry.get().strip()
        if not data:
            messagebox.showwarning("Input needed", "Please enter text or URL to generate QR code.")
            return
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # Convert to Tkinter image
        bio = io.BytesIO()
        img.save(bio, format='PNG')
        bio.seek(0)
        tk_img = ImageTk.PhotoImage(Image.open(bio))

        self.qr_label.config(image=tk_img)
        self.qr_label.image = tk_img

        # Save current QR in memory
        self.qr_images.append((data, img.copy(), tk_img))

        # Update listbox
        self.listbox.insert(tk.END, data)

        # Enable buttons
        self.save_button.config(state='normal')
        self.share_button.config(state='normal')

    def on_select(self, event):
        if not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        data, pil_img, tk_img = self.qr_images[index]
        self.qr_label.config(image=tk_img)
        self.qr_label.image = tk_img
        self.entry.delete(0, tk.END)
        self.entry.insert(0, data)

        # Enable buttons
        self.save_button.config(state='normal')
        self.share_button.config(state='normal')

    def save_qr(self):
        if not self.qr_label.image:
            messagebox.showinfo("No QR Code", "Generate a QR code first!")
            return
        
        index = self.get_current_qr_index()
        if index is None:
            messagebox.showerror("Error", "Please select a QR code to save.")
            return
        
        data, pil_img, _ = self.qr_images[index]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialfile=f"qrcode_{data[:10].replace(' ','_')}.png",
            title="Save QR Code"
        )
        if file_path:
            pil_img.save(file_path)
            messagebox.showinfo("Saved", f"QR code saved to:\n{file_path}")

    def share_qr(self):
        # Open saved image in default viewer for "sharing"
        index = self.get_current_qr_index()
        if index is None:
            messagebox.showerror("Error", "Please select a QR code to open/share.")
            return
        
        data, pil_img, _ = self.qr_images[index]
        # Save to temp file
        temp_path = os.path.join(os.path.expanduser("~"), f"temp_qrcode_{data[:10].replace(' ','_')}.png")
        pil_img.save(temp_path)

        # Open file using OS default viewer
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', temp_path))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(temp_path)
        else:                                   # Linux variants
            subprocess.call(('xdg-open', temp_path))

    def get_current_qr_index(self):
        # Try to find current QR index by matching label image ref
        current_img = self.qr_label.image
        for idx, (_, _, tk_img) in enumerate(self.qr_images):
            if tk_img == current_img:
                return idx
        return None

if __name__ == "__main__":
    app = tk.Tk()
    QRApp(app)
    app.mainloop()
