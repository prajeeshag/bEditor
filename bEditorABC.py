
from abc import ABC, abstractmethod
from tkinter import Button, Entry, Frame, Label, StringVar, Toplevel, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

class BathymetryEditorBase(ABC):
    def __init__(self, root):
        self.root = root
        self.root.title("Bathymetry Data Editor")
        self.root.geometry("1000x800")  # Set the window size

        self.frame = Frame(root, pady=10)
        self.frame.pack()

        button_font = ("Helvetica", 12)

        self.load_button = Button(self.frame, text="Load Data", command=self.load_data, font=button_font)
        self.load_button.pack(side="left", padx=5)

        self.save_button = Button(self.frame, text="Save Data", command=self.save_data, font=button_font)
        self.save_button.pack(side="left", padx=5)

        self.find_islands_button = Button(self.frame, text="Find Islands", command=self.find_islands, font=button_font)
        self.find_islands_button.pack(side="left", padx=5)

        self.find_lakes_button = Button(self.frame, text="Find Lakes", command=self.find_lakes, font=button_font)
        self.find_lakes_button.pack(side="left", padx=5)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.bathymetry_data = None
        self.patches = []

    def load_data_from_args(self, nx, ny, bathy_path):
        try:
            self.bathymetry_data = np.fromfile(bathy_path, ">f4").reshape(ny, nx)
            self.update_canvas()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")

    def load_data(self):
        NX, NY = self.custom_input_dialog("Enter NX and NY", ["NX (number of columns):", "NY (number of rows):"])
        if NX and NY:
            file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])
            if file_path:
                self.load_data_from_args(int(NX), int(NY), file_path)

    def save_data(self):
        if self.bathymetry_data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".npy", filetypes=[("Numpy Files", "*.npy")])
            if file_path:
                np.save(file_path, self.bathymetry_data)
        else:
            messagebox.showerror("Error", "No data to save")

    def update_canvas(self):
        if self.bathymetry_data is not None:
            self.ax.clear()
            self.ax.imshow(self.bathymetry_data, cmap='terrain', origin='lower')
            self.canvas.draw()

    def on_click(self, event):
        if self.edit_mode and self.bathymetry_data is not None:
            x, y = int(event.xdata), int(event.ydata)
            # Implement pixel editing functionality
            pass

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode

    def custom_input_dialog(self, title, prompts):
        dialog = Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("600x300")

        entries = []
        for i, prompt in enumerate(prompts):
            label = Label(dialog, text=prompt, font=("Helvetica", 12))
            label.grid(row=i, column=0, pady=5, padx=5)
            var = StringVar()
            entry = Entry(dialog, textvariable=var, font=("Helvetica", 12))
            entry.grid(row=i, column=1, pady=5, padx=5)
            entries.append(var)

        def on_ok():
            dialog.destroy()

        ok_button = Button(dialog, text="OK", command=on_ok, font=("Helvetica", 12))
        ok_button.grid(row=len(prompts), column=0, columnspan=2, pady=10)

        dialog.grab_set()
        self.root.wait_window(dialog)

        return [e.get() for e in entries]

    @abstractmethod
    def find_islands(self):
        pass

    @abstractmethod
    def find_lakes(self):
        pass