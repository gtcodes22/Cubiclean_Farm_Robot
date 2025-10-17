# requires matlab engine, pillow
#
import matlab.engine
from PIL import Image



# Start MATLAB engine
eng = matlab.engine.start_matlab()

# Add the folder where your MATLAB function is located
folder = eng.uigetdir()
if folder == 0:
    print("error: user didn't select a folder")
    eng.quit()
    exit()
    
eng.addpath(folder)
#eng.addpath(r'C:\Users\ramee\OneDrive\Documents\Group Project\MATLAB')

# set variables for test script
a = int(input("enter value for a "))
b = int(input("enter value for b "))

# Create a filepath
filename = folder + r'\my_plot.jpg'

# Call the MATLAB function
eng.create_plot(a,b,filename,nargout=0)

# Open saved image in python
img = Image.open(filename)
img.show()

# Stop MATLAB engine
eng.quit()