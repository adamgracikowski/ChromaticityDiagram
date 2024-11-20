import pandas as pd # type: ignore
import numpy as np # type: ignore
from scipy.interpolate import interp1d # type: ignore
from scipy.special import comb # type: ignore

class ChromaticityCalculator:
    def __init__(self, n):
        self.wavelengths = None
        self.x = None
        self.y = None
        self.z = None
        self.lambda_min = None
        self.lambda_max = None
        self.control_points = None
        self.curve = None
        self.n = n
        
    def load_matching_functions(self, filename):
        try:
            data = pd.read_csv(filename, sep=r'\s+')
            
            if not {'wavelength', 'x', 'y', 'z'}.issubset(data.columns):
                raise ValueError("The file must contain the following columns: 'wavelength', 'x', 'y', 'z'.")
            
            self.wavelengths = data['wavelength']
            self.x = data['x']
            self.y = data['y']
            self.z = data['z']
            
            self.lambda_min = min(self.wavelengths)
            self.lambda_max = max(self.wavelengths)
            self.control_points = self.generate_control_points(self.n)
            self.curve = self.generate_bezier_curve(self.lambda_max - self.lambda_min)
        except FileNotFoundError:
            print(f"Error: File {filename} was not found.")
            raise
        except Exception as e:
            print(f"Error: {e}")
            raise
           
    def _interpolate_functions(self, wavelengths_target, wavelengths_source, values_source):
        interpolator = interp1d(wavelengths_source, values_source, kind='linear', fill_value="extrapolate")
        return interpolator(wavelengths_target)
 
    def spectral_to_XYZ(self, P, target_wavelengths):   
        x_interp = self._interpolate_functions(target_wavelengths, self.wavelengths, self.x)
        y_interp = self._interpolate_functions(target_wavelengths, self.wavelengths, self.y)
        z_interp = self._interpolate_functions(target_wavelengths, self.wavelengths, self.z)
        
        # k = 1 / ∫ P(λ) * ȳ(λ) dλ
        normalization_factor = np.trapezoid(P * y_interp, target_wavelengths)
        k = 1 / normalization_factor

        X = k * np.trapezoid(P * x_interp, target_wavelengths)
        Y = k * np.trapezoid(P * y_interp, target_wavelengths)
        Z = k * np.trapezoid(P * z_interp, target_wavelengths)
        
        return X, Y, Z
    
    def tristimulus_coefficients(self, X, Y, Z):
        total = X + Y + Z
        x = X / total
        y = Y / total
        return x, y, Y
    
    def generate_control_points(self, num_points):
        return np.array([
            [
                self.lambda_min + i * (self.lambda_max - self.lambda_min) / num_points, 
                np.random.uniform(0, 1)
            ]
            for i in range(num_points + 1)
        ])
        
    def generate_bezier_curve(self, num_points):
        n = len(self.control_points) - 1
        t_min = self.control_points[0][0]
        t_max = self.control_points[-1][0]
        t = np.linspace(t_min, t_max, num_points)
        normalized_t = (t - t_min) / (t_max - t_min)
        curve = np.zeros((num_points, 2))
        
        for i in range(n + 1):
            binomial = comb(n, i) * (normalized_t ** i) * ((1 - normalized_t) ** (n - i))
            curve += binomial[:, None] * self.control_points[i]
            
        return np.column_stack((t, curve[:, 1]))
    
    def update_control_point(self, index, x, y):
        n = len(self.control_points)
        if index == n - 1:
            x = self.control_points[index][0]
        elif index == 0:
            x = self.control_points[index][0]
        else:
            x = self.clamp(
                x,
                self.control_points[index - 1][0],
                self.control_points[index + 1][0]
            )
        
        self.control_points[index] = [x, y]
             
    def clamp(self, value, min_value, max_value):
        return max(min(value, max_value), min_value)