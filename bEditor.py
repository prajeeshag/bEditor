import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from tkinter import Tk, Button, Frame, filedialog, messagebox, Toplevel, Label, Entry, StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import typer

app_cli = typer.Typer()



def flood_fill(data, x, y, target_value, replacement_value):
    rows, cols = data.shape
    if data[x, y] != target_value:
        return []

    to_fill = [(x, y)]
    filled = []

    while to_fill:
        x, y = to_fill.pop()
        if data[x, y] == target_value:
            data[x, y] = replacement_value
            filled.append((x, y))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols and data[nx, ny] == target_value:
                    to_fill.append((nx, ny))
    
    return filled


class BathymetryEditor:
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
        
        self.find_channels_button = Button(self.frame, text="Find Channels", command=self.find_channels, font=button_font)
        self.find_channels_button.pack(side="left", padx=5)
        
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
                self.load_data_from_args(NX,NY,file_path)

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
        dialog.geometry("300x150")

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

    def find_islands(self):
        self.patches = []
        rows, cols = self.bathymetry_data.shape
        visited = np.zeros_like(self.bathymetry_data, dtype=bool)
        for x in range(rows):
            for y in range(cols):
                if self.bathymetry_data[x, y] >= 0 and not visited[x, y]:
                    land_mass = flood_fill(self.bathymetry_data, x, y, self.bathymetry_data[x, y], -9999)
                    if all(self.bathymetry_data[nx, ny] < 0 for nx, ny in land_mass):
                        cx, cy = np.mean(land_mass, axis=0)
                        circle = Circle((cy, cx), 5, color='red', fill=False)
                        self.ax.add_patch(circle)
                        self.patches.append(circle)
                    for nx, ny in land_mass:
                        visited[nx, ny] = True
        self.canvas.draw()

    def find_lakes(self):
        self.patches = []
        rows, cols = self.bathymetry_data.shape
        visited = np.zeros_like(self.bathymetry_data, dtype=bool)
        for x in range(rows):
            for y in range(cols):
                if self.bathymetry_data[x, y] < 0 and not visited[x, y]:
                    water_body = flood_fill(self.bathymetry_data, x, y, self.bathymetry_data[x, y], 9999)
                    if all(self.bathymetry_data[nx, ny] >= 0 for nx, ny in water_body):
                        cx, cy = np.mean(water_body, axis=0)
                        circle = Circle((cy, cx), 5, color='blue', fill=False)
                        self.ax.add_patch(circle)
                        self.patches.append(circle)
                    for nx, ny in water_body:
                        visited[nx, ny] = True
        self.canvas.draw()

    def find_channels(self):
        W = int(self.width_entry.get())
        L = int(self.length_entry.get())
        self.patches = []
        rows, cols = self.bathymetry_data.shape
        for x in range(rows):
            for y in range(cols):
                if self.bathymetry_data[x, y] < 0:
                    for dx, dy in [(0, 1), (1, 0)]:
                        nx, ny = x + dx * L, y + dy * W
                        if nx < rows and ny < cols and all(self.bathymetry_data[x + i * dx, y + i * dy] < 0 for i in range(L)) and \
                                all(self.bathymetry_data[x + i * dx + dy, y + i * dy + dx] >= 0 for i in range(W)) and \
                                all(self.bathymetry_data[x + i * dx - dy, y + i * dy - dx] >= 0 for i in range(W)):
                            for i in range(L):
                                circle = Circle((y + i * dy, x + i * dx), 1, color='green', fill=False)
                                self.ax.add_patch(circle)
                                self.patches.append(circle)
        self.canvas.draw()



@app_cli.command()
def main(nx: int = typer.Option(None, "--nx", help="Number of columns"),
         ny: int = typer.Option(None, "--ny", help="Number of rows"),
         bathy: str = typer.Option(None, "--bathy", help="Path to bathymetry binary file")):
    root = Tk()
    app = BathymetryEditor(root)
    
    if nx and ny and bathy:
        app.load_data_from_args(nx, ny, bathy)

    root.mainloop()




if __name__ == "__main__":
    app_cli()