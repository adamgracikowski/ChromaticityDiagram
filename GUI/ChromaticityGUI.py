import matplotlib.pyplot as plt # type: ignore
from matplotlib.widgets import Slider # type: ignore
import matplotlib.image as mpimg

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
        self.ax1.set_title("Bézier curve")
        self.ax1.set_xlabel("Wavelength (nm)")
        self.ax1.set_ylabel("Amplitude")
        self.ax1.legend()
        
    def configure_ax2(self):
        self.plot_cie_diagram()
        self.ax2.set_xlim(0, 1)
        self.ax2.set_ylim(0, 1)
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
        img = mpimg.imread('Assets/CIE1931.png')
        self.ax2.imshow(img, extent=[0, 0.777, 0, 0.834], aspect='auto')
        # denominator = self.chromaticity_calculator.x + \
        #     self.chromaticity_calculator.y + \
        #     self.chromaticity_calculator.z
        # x = self.chromaticity_calculator.x / denominator
        # y = self.chromaticity_calculator.y / denominator
        # wavelengths = self.chromaticity_calculator.wavelengths
        
        # mask = (
        #     np.isnan(x) | 
        #     np.isnan(y) | 
        #     (x <= 0) | 
        #     (x >= 0.7436) | 
        #     (y <= 0) | 
        #     (y >= 1)
        # )

        # x = x[~mask].tolist()
        # y = y[~mask].tolist()
        # wavelengths = wavelengths[~mask]
        
        # colors = plt.cm.plasma(
        #     (wavelengths - self.chromaticity_calculator.lambda_min) / 
        #     (self.chromaticity_calculator.lambda_max - self.chromaticity_calculator.lambda_min)
        # )

        # self.ax2.scatter(x, y, c=colors, edgecolor='none')
    
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