from flask import Flask, render_template, request, redirect, url_for
from flask_babel import Babel, _
import signal
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
from scipy.integrate import odeint
from io import BytesIO
import base64
import tempfile
import os
import geopandas as gpd
from imgen import generate_spiral_image
from pendgen import simulate_double_pendulum, create_pendulum_animation
import threading
import time

plt.switch_backend('Agg')

app = Flask(__name__)

# Configuration for Flask-Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'de']

babel = Babel()

def get_locale():
    # Check if the user has selected a language
    return request.args.get('lang') or request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

babel.init_app(app, locale_selector=get_locale)

#generate the spiral for the header
filename = 'static/spiral.png'  # Path to save the image
generate_spiral_image(filename)
print("Spiral generated!")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/switch_language/<language>')
def switch_language(language):
    # Set the language using a URL parameter
    return redirect(url_for('index', lang=language))

@app.route('/personal')
def personal():
    return render_template('personal.html')

@app.route('/styletest')
def test():
    # Generate sample data (you can replace this with your actual data retrieval logic)
    data = {'Category': ['A', 'B', 'C', 'D'],
            'Values': [10, 30, 20, 25]}
    
    df = pd.DataFrame(data)
    
    # Create a simple bar plot
    plt.figure(figsize=(10, 6))
    plt.bar(df['Category'], df['Values'], color='seagreen')
    plt.xlabel('Category')
    plt.ylabel('Values')
    plt.title('Simple Bar Graph')
    plt.tight_layout()

    # Save plot to a bytes object
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)

    # Encode plot as base64 string
    plot_url = base64.b64encode(img_bytes.read()).decode('utf8')
    
    # Clear the figure to release resources
    plt.clf()
    plt.close()

    return render_template('test.html', plot_url=plot_url)

@app.route('/graph')
def graph():
    # Generate sample data (you can replace this with your actual data retrieval logic)
    data = {'Category': ['A', 'B', 'C', 'D'],
            'Values': [10, 30, 20, 25]}
    
    df = pd.DataFrame(data)
    
    # Create a simple bar plot
    plt.figure(figsize=(10, 6))
    plt.bar(df['Category'], df['Values'], color='skyblue')
    plt.xlabel('Category')
    plt.ylabel('Values')
    plt.title('Simple Bar Graph')
    plt.tight_layout()

    # Save plot to a bytes object
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)

    # Encode plot as base64 string
    plot_url = base64.b64encode(img_bytes.read()).decode('utf8')
    
    # Clear the figure to release resources
    plt.clf()
    plt.close()

    # Create second plot - Polar plot (Cardioid)
    # Generate data for the polar plot
    theta = np.linspace(0, 2 * np.pi, 1000)
    r = (1 - 10 * np.sin(theta))
    
    # Plotting the cardioid in polar coordinates
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, projection='polar')
    ax.plot(theta, r)
    
    ax.set_title("Cardioid")
    ax.grid(True)
    ax.set_yticks([1])
    plt.tight_layout()

    # Save plot to a bytes object
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)

    # Encode plot as base64 string
    plot_url1 = base64.b64encode(img_bytes.read()).decode('utf8')

    # Clear the figure to release resources
    plt.clf()
    plt.close()

    return render_template('graph.html', plot_url=plot_url, plot_url1 = plot_url1)


@app.route('/map')
def map():
    # Load GeoJSON file using Geopandas
    geojson_path = 'static/Counties.geojson'
    gdf = gpd.read_file(geojson_path)

    # Create a simple plot of the GeoDataFrame
    fig, ax = plt.subplots(figsize=(10, 8))
    gdf.plot(ax=ax, edgecolor='black', cmap='YlGnBu', column = "SHAPEAREA", legend=True)
    ax.set_title('Counties in Wisconsin')

    # Legend issues
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, title="Area in Square Meters", loc="best")
    
    ax.set_axis_off()

    # Save plot to a bytes object
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)

    # Encode plot as base64 string
    plot_url = base64.b64encode(img_bytes.read()).decode('utf8')

    return render_template('map.html', plot_url=plot_url)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Collect answers from the form
        answers = [
            request.form.get('q1'),
            request.form.get('q2'),
            request.form.get('q3'),
            request.form.get('q4'),
            request.form.get('q5')
        ]
        
        # Calculate the result
        stem_count = answers.count('stem')
        business_count = answers.count('business')
        
        # Redirect based on the count
        if stem_count > business_count:
            return redirect(url_for('result_stem'))
        else:
            return redirect(url_for('result_business'))
    
    return render_template('quiz.html')

@app.route('/major')
def major():
    return render_template('major.html')

@app.route('/result_stem')
def result_stem():
    return render_template('result_stem.html')

@app.route('/result_business')
def result_business():
    return render_template('result_business.html')
    
#mods
t = None
solution = None
plot_url = None
animation_thread = None

# Function to simulate the double pendulum and start animation thread
def initialize_pendulum_simulation():
    global t, solution
    t, solution = simulate_double_pendulum(np.pi / 4, np.pi / 6)
    print("Pendulum simulated!")

    # Start animation thread
    start_animation_thread()

def sim():
    global plot_url
    plot_url = create_pendulum_animation(t, solution)
    print("Animation completed")

def start_animation_thread():
    global animation_thread
    animation_thread = threading.Thread(target=sim)
    animation_thread.start()

# Initialize the double pendulum simulation and animation thread
initialize_pendulum_simulation()

@app.route('/double_pendulum')
def double_pendulum():
    global plot_url
    if plot_url is None:
        return "Animation loading. Please refresh in a moment."
    else:
        return render_template('double_pendulum.html', plot_url=plot_url)

def signal_handler(signal, frame):
    print('Flask application shutting down...')
    # Perform any cleanup actions if needed
    # For example, close database connections, etc.
    exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    app.run(threaded=True, debug=True)
