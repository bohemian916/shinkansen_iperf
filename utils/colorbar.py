import numpy as np

def sigmoid(x, gain=1, offset_x=0):
    return ((np.tanh(((x + offset_x) * gain) / 2) + 1) / 2)
 
def colorBarRGB(x, offset_x, offset_green):
    gain = 30
    x = (x * 2) - 1
    red = sigmoid(x, gain, -1 * offset_x)
    blue = 1 - sigmoid(x, gain, offset_x)
    green = sigmoid(x, gain, offset_green) + (1 - sigmoid(x, gain, -1 * offset_green))
    green = green - 1.0
    return (red * 256, green * 256, blue * 256)


