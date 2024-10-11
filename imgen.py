import matplotlib.pyplot as plt
import numpy as np

def generate_spiral_image(filename):
    # Parameters for the spiral
    theta = np.linspace(0, 8 * np.pi, 1000)  # Angle
    z = np.linspace(0, 1, 1000)  # Height
    r = z ** 4  # Radius

    # Convert polar coordinates to cartesian coordinates
    x = r * np.sin(theta)
    y = r * np.cos(theta)

    # Plotting the spiral
    fig, ax = plt.subplots(figsize=(16, 4))
    ax.plot(x, y, color='blue')
    ax.plot(-x, -y, color='firebrick')  # Mirror image

    # Set background color to gray
    ax.set_facecolor('#808080')
    fig.patch.set_facecolor('#808080')

    # Remove axes
    ax.axis('off')

    # Save the figure
    plt.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close()
