from tkinter import Tk
import typer
import numpy as np
from matplotlib.patches import Circle
from scipy.ndimage import label
from utils import *
from bEditorABC import BathymetryEditorBase

app_cli = typer.Typer()





class BathymetryEditor(BathymetryEditorBase):
    def __init__(self, root):
        super().__init__(root)
        self._lmask = None

    @property
    def lmask(self):
        if self.bathymetry_data is not None:
            return self.bathymetry_data >= 0
        return None
    
    def find_features(self, mask, color):
        for patch in self.patches:
            patch.remove()
        self.patches.clear()

        labeled_array, num_features = label(mask)
        for feature_num in range(1, num_features + 1):
            feature_mask = (labeled_array == feature_num)
            coords = np.argwhere(feature_mask)
            #cx, cy = np.mean(coords, axis=0)
            cx, cy = geometric_median(coords)
            circle = Circle((cy, cx), 5, color=color, fill=False)
            self.ax.add_patch(circle)
            self.patches.append(circle)
        self.canvas.draw()

    def find_islands(self):
        if self.lmask is not None:
            self.find_features(self.lmask, 'red')

    def find_lakes(self):
        if self.lmask is not None:
            inverted_lmask = ~self.lmask
            self.find_features(inverted_lmask, 'blue')

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