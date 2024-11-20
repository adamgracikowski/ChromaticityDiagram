import sys
from GUI.ChromaticityGUI import ChromaticityGUI

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python chromaticity_diagram.py <filename> <n>")
        sys.exit(1)

    filename = sys.argv[1]
    
    try:
        n = int(sys.argv[2])
    except ValueError:
        print("Error: Degree of the curve must be an integer.")
        sys.exit(1)
        
    gui = ChromaticityGUI(filename, n)
    gui.run()