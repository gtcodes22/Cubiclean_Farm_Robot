# -*- coding:utf-8 -*-
'''!
  @file import math.py
  @brief Imports the MATLAB engine and runs the script in the folder. which
  @n produces an output image.
  @author Rameez Shiekh
  @maintainer Jade Cawley
  @version  V1.1
  @data 2026-02-18
'''

# libraries 2
import matlab.engine
from PIL import Image
from os import getcwd

def main():
    # Start MATLAB engine
    eng = matlab.engine.start_matlab()
    
    # get MATLAB folder inside current folder
    workingDir = getcwd() + '\\MATLAB'
    
    # Add the folder where the MATLAB function is located
    eng.addpath(workingDir)

    # prompt user for inputs
    a = int(input("enter value for a "))
    b = int(input("enter value for b "))

    # Create a filepath
    # TODO: create new image file without overwritting previous?
    filename = workingDir + '\\my_plot.jpg'

    # Call the MATLAB function
    eng.create_plot(a,b,filename,nargout=0)

    # Open saved image in python
    img = Image.open(filename)
    img.show()

    # Stop MATLAB engine
    eng.quit()
    
# run main function if file directly executed    
if __name__ == "__main__":
    main()