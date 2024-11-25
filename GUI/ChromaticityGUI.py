import matplotlib.pyplot as plt # type: ignore
from matplotlib.widgets import Slider # type: ignore
import matplotlib.image as mpimg
import numpy as np

from Calculators.ChromaticityCalculator import ChromaticityCalculator

class ChromaticityGUI:
    def __init__(self, filename, n):
        self.chromaticity_calculator = ChromaticityCalculator(n)
        self.chromaticity_calculator.load_matching_functions(filename)
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.ax_slider = plt.axes([0.2, 0.0001, 0.6, 0.03], facecolor='lightgoldenrodyellow')
        self.degree_slider = Slider(self.ax_slider, 'Degree', 1, 30, valinit=n, valstep=1)
        self.degree_slider.on_changed(self.update_degree)
        self.dragging_point = None
        self.control_scatters = None
        self.bezier_line = None
        self.spectral_scatter = None
        self.control_line = None
    
    def run(self):
        self.bezier_line, = self.ax1.plot(
            self.chromaticity_calculator.curve[:, 0], 
            self.chromaticity_calculator.curve[:, 1], 
            label="Bézier curve")
        
        self.control_scatters = self.ax1.scatter(
            self.chromaticity_calculator.control_points[:, 0], 
            self.chromaticity_calculator.control_points[:, 1], 
            color='red', 
            label="Control points"
        )
        
        self.control_line, = self.ax1.plot(
            self.chromaticity_calculator.control_points[:, 0],
            self.chromaticity_calculator.control_points[:, 1],
            linestyle='--',
            color='gray'
        )
        
        self.spectral_scatter = self.ax2.scatter([], [], color='blue')

        self.configure_ax1()
        self.configure_ax2()
        
        self.plot_cie_diagram()
        self.update()

        self.fig.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('button_release_event', self.on_button_release)

        plt.tight_layout()
        plt.show()
      
    def configure_ax1(self):
        zoom = 20
        self.ax1.set_ylim(0, 1)
        self.ax1.set_xlim(
            self.chromaticity_calculator.lambda_min - zoom, 
            self.chromaticity_calculator.lambda_max + zoom
        )
        self.ax1.set_facecolor((0.94, 0.94, 0.94))
        self.ax1.set_title("Bézier curve")
        self.ax1.set_xlabel("Wavelength (nm)")
        self.ax1.set_ylabel("Amplitude")
        self.ax1.legend()
        
    def configure_ax2(self):
        self.plot_cie_diagram()
        self.ax2.set_xlim(0, 1)
        self.ax2.set_ylim(0, 1)
        self.ax2.set_facecolor((0.94, 0.94, 0.94))
        self.ax2.set_title("Chromaticity Diagram")
        self.ax2.set_xlabel("x")
        self.ax2.set_ylabel("y")
            
    def on_button_press(self, event):
        if event.inaxes == self.ax1 and event.button == 1:
            x, y = event.xdata, event.ydata
            for i, (cx, cy) in enumerate(self.chromaticity_calculator.control_points):
                if abs(cx - x) < 15 and abs(cy - y) < 0.05:
                    self.dragging_point = i
                    break
                
    def on_mouse_move(self, event):
        if self.dragging_point is not None and event.inaxes == self.ax1:
            x, y = event.xdata, event.ydata
            self.chromaticity_calculator.update_control_point(self.dragging_point, x, y)
            self.update()
            
    def on_button_release(self, event):
        if event.button == 1:
            self.dragging_point = None
    
    def plot_cie_diagram(self):
        try:
            img = mpimg.imread('Assets/CIE1931.png')
            self.ax2.imshow(img, extent=[0, 0.777, 0, 0.834], aspect='auto')
        except FileNotFoundError:
            print("Error: File 'Assets/CIE1931.png' not found. Ensure the path is correct.")
            return
        
        denominator = self.chromaticity_calculator.x + \
            self.chromaticity_calculator.y + \
            self.chromaticity_calculator.z
            
        mask = denominator > 0
        
        denominator = denominator[mask]
        x = self.chromaticity_calculator.x[mask] / denominator
        y = self.chromaticity_calculator.y[mask] / denominator
        z = self.chromaticity_calculator.z[mask] / denominator
        
        mask = (
            np.isnan(x) | 
            np.isnan(y) | 
            (x <= 0) | 
            (x >= 0.7436) | 
            (y <= 0) | 
            (y >= 1)
        )
        
        x = x[~mask]
        y = y[~mask]
        z = z[~mask]

        colors = [
            self.convert_xyz_to_rgb(x_val, y_val, z_val)
            for x_val, y_val, z_val in zip(x, y, z)
        ]
        
        normalized_colors = [
            (r / 255, g / 255, b / 255) for r, g, b in colors
        ]
         
        self.ax2.scatter(x, y, c=normalized_colors, edgecolor='none', s=10)
    
    def convert_xyz_to_rgb(self, x, y, z):
        r = 3.2410 * x - 1.5374 * y - 0.4986 * z
        g = -0.9692 * x + 1.8760 * y + 0.0416 * z
        b = 0.0556 * x - 0.2040 * y + 1.0570 * z

        def gamma_correction(value):
            if value > 0.0031308:
                return 1.055 * (value ** (1.0 / 2.4)) - 0.055
            else:
                return 12.92 * value

        r = int(max(0, min(1, gamma_correction(r))) * 255)
        g = int(max(0, min(1, gamma_correction(g))) * 255)
        b = int(max(0, min(1, gamma_correction(b))) * 255)

        return r, g, b
    
    def update(self):
        self.chromaticity_calculator.curve = self.chromaticity_calculator.generate_bezier_curve(
            self.chromaticity_calculator.lambda_max - self.chromaticity_calculator.lambda_min
        )
        
        X, Y, Z = self.chromaticity_calculator.spectral_to_XYZ(
            self.chromaticity_calculator.curve[:, 1],
            self.chromaticity_calculator.curve[:, 0],
        )
        
        x, y, Y = self.chromaticity_calculator.tristimulus_coefficients(X, Y, Z)
                
        self.bezier_line.set_data(
            self.chromaticity_calculator.curve[:, 0], 
            self.chromaticity_calculator.curve[:, 1]
        )
        
        self.control_line.set_data(
            self.chromaticity_calculator.control_points[:, 0],
            self.chromaticity_calculator.control_points[:, 1]
        )
        
        self.control_scatters.set_offsets(self.chromaticity_calculator.control_points)
        
        self.update_cie_diagram(x, y)
        self.fig.canvas.draw_idle()

    def update_cie_diagram(self, x, y):
        self.spectral_scatter.set_offsets([[x, y]])
        
        for artist in self.ax2.texts:
            artist.remove()
        
        self.ax2.annotate(
            f"({x:.4f}, {y:.4f})",
            (x, y),
            textcoords="offset points", 
            xytext=(5, 5),
            fontsize=8,
            color="blue"
        )
   
    def update_degree(self, val):
        degree = int(val)
        self.chromaticity_calculator.control_points = self.chromaticity_calculator.generate_control_points(degree)
        self.update()