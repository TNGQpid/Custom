#Double Pendulum Code (it's gonna be long)
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
from scipy.integrate import odeint
from io import BytesIO
import base64
import tempfile
import os

def double_pendulum_derivatives(y, t, L1, L2, m1, m2, g):
    theta1, z1, theta2, z2 = y
    cos_delta = np.cos(theta1 - theta2)
    sin_delta = np.sin(theta1 - theta2)
    
    denominator1 = (m1 + m2) * L1 - m2 * L1 * cos_delta**2
    denominator2 = (L2/L1) * denominator1
    
    dydt = [
        z1,
        (m2 * L1 * z1**2 * sin_delta * cos_delta +
         m2 * g * np.sin(theta2) * cos_delta +
         m2 * L2 * z2**2 * sin_delta -
         (m1 + m2) * g * np.sin(theta1)) / denominator1,
        z2,
        (-m2 * L2 * z2**2 * sin_delta * cos_delta +
         (m1 + m2) * g * np.sin(theta1) * cos_delta -
         (m1 + m2) * L1 * z1**2 * sin_delta -
         (m1 + m2) * g * np.sin(theta2)) / denominator2
    ]
    return dydt

def simulate_double_pendulum(theta1, theta2, L1=1.0, L2=1.0, m1=1.0, m2=1.0, g=9.8, t_max=7.0, dt=0.01):
    y0 = [theta1, 0.0, theta2, 0.0]
    t = np.arange(0, t_max + dt, dt)
    solution = odeint(double_pendulum_derivatives, y0, t, args=(L1, L2, m1, m2, g))
    return t, solution

def create_pendulum_animation(t, solution, L1=1.0, L2=1.0, trace_step = 4):
    theta1 = solution[:, 0]
    theta2 = solution[:, 2]

    x1 = L1 * np.sin(theta1)
    y1 = -L1 * np.cos(theta1)
    x2 = x1 + L2 * np.sin(theta2)
    y2 = y1 - L2 * np.cos(theta2)

    fig, ax = plt.subplots(figsize=(8, 8), dpi = 80)
    ax.set_xlim(-L1 - L2 - 0.5, L1 + L2 + 0.5)
    ax.set_ylim(-L1 - L2 - 0.5, L1 + L2 + 0.5)
    ax.set_aspect('equal')

    line, = ax.plot([], [], 'o-', lw=2)
    trace, = ax.plot([], [], 'r-', lw=1, alpha=0.5)

    def init():
        line.set_data([], [])
        trace.set_data([], [])
        return line, trace

    def update(i):
        thisx = [0, x1[i], x2[i]]
        thisy = [0, y1[i], y2[i]]
        line.set_data(thisx, thisy)
        trace.set_data(x2[:i], y2[:i])
        return line, trace

    anim = FuncAnimation(fig, update, frames=len(t), init_func=init, blit=True)

    # Save the animation to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as tmpfile:
        anim.save(tmpfile.name, writer=PillowWriter(fps=30))
        tmpfile_path = tmpfile.name

    # Read the temporary file into a BytesIO object
    with open(tmpfile_path, 'rb') as f:
        img_bytes = BytesIO(f.read())

    # Clean up the temporary file
    os.remove(tmpfile_path)

    plot_url = base64.b64encode(img_bytes.getvalue()).decode('utf8')
    plt.close(fig)
    return plot_url
