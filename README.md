# Chromaticity Diagram

The Chromaticity Diagram project is an interactive application that visualizes spectral distribution curves using Bézier curves and maps their chromaticity coordinates onto a chromaticity diagram.

The project was implemented as a part of the Computer Graphics course at Warsaw University of Technology during the winter semester of the 2024-2025 academic year.

This tool is designed for educational purposes, helping users understand the relationship between spectral distribution and chromaticity.

## Features:

- **Interactivity**: User can interactively modify the spectral distribution curve by adjusting the positions of its control points.
- **Adjustable Degree**: The degree of the Bézier curve can be dynamically changed to explore different curve complexities.
- **Chromaticity Diagram**: The chromaticity point updates in real-time as the shape of the Bézier curve changes.

## Technologies Used:

- **Python**: For the core logic and computations.
- **Matplotlib**: For rendering the spectral distribution plot and chromaticity diagram.
- **NumPy**: For efficient mathematical operations, including Bézier curve calculations.

## Getting Started:

1. Clone the repository to your local machine:

```bash
git clone https://github.com/adamgracikowski/ChromaticityDiagram.git
```

2. Install all the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python chromaticity_diagram.py <filename> <degree_of_the_curve>
```

For example:

```bash
python chromaticity_diagram.py 'Assets/CIE1931.txt' 6
```
