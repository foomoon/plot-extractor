import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patheffects as path_effects


def plot_median(median, data_points):
        """Plots the median RCS value as a horizontal line on the graph."""
        plt.axhline(y=median, color='r', linestyle='--', label=f'Median: {median:.1f}')
        # add text annotation for median centered above line
        x = (min(data_points[:,0]) + max(data_points[:,0])) / 2
        draw_outlined_text(x, median, f'Median: {median:.1f}', color='red', ha='center', va='center')

def draw_outlined_text(x, y, text, color='black', outline_color='white', ha='left', va='top', fontsize=12, fontweight='bold'):
    """Draws text with an outline to make it stand out on both dark and light backgrounds."""
    plt.text(x, y, text, ha=ha, va=va, fontsize=fontsize, fontweight=fontweight, color=outline_color, path_effects=[path_effects.withStroke(linewidth=3, foreground=outline_color)])
    plt.text(x, y, text, ha=ha, va=va, fontsize=fontsize, fontweight=fontweight, color=color)


def generate_sample_figure(settings):
    """Generates a plot with the given data and settings, and saves it to a file."""
    title = settings.get("title", "Sample Plot")
    x_label = settings.get("x_label", "X Axis")
    y_label = settings.get("y_label", "Y Axis")
    type_text = settings.get("type", "SAMPLE")
    line_width = settings.get("line_width",0.5)
    x_min, x_max = settings.get("x_lim", [0, 180])
    y_min, y_max = settings.get("y_lim", [-30, 30])


    # Create the figure and axis with a white background
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='white')

    # Add grid, title, and axis labels in black
    ax.grid(True, linestyle='--', linewidth=line_width, color='gray')
    ax.set_title(title, color='black')
    ax.set_xlabel(x_label, color='black')
    ax.set_ylabel(y_label, color='black')

    # Set x-axis ticks and axis limits
    ax.set_xticks(np.arange(0, 181, 20))
    # ax.set_xlim(0, 180)
    # ax.set_ylim(-30, 30)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Ensure tick labels are black
    ax.tick_params(colors='black')

    # Adjust subplot parameters to leave room inside the figure
    fig.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.15)

    # Add an outer black border inset from the figure edge.
    border = Rectangle((0.05, 0.05), 0.9, 0.9, fill=False,
                       transform=fig.transFigure, clip_on=False,
                       linewidth=2, edgecolor='black')
    fig.patches.append(border)

    # Add the text "SAMPLE" to the top left and bottom right of the figure
    fig.text(0.06, 0.94, type_text, ha="left", va="top", color='black', fontsize=12, fontweight='bold')
    fig.text(0.94, 0.06, type_text, ha="right", va="bottom", color='black', fontsize=12, fontweight='bold')

    return ax

if __name__ == "__main__":
    

    # Define plot settings
    settings = {
        "title": "Sample Sine Wave",
        "x_label": "Aspect Angle (deg)",
        "y_label": "RCS (dBsm)",
        "type": "SAMPLE",
    }

    filename="input/sample2.png"

    # Generate the sample figure
    ax = generate_sample_figure(settings)

    # Generate sample data
    x = np.linspace(10, 170, 300)
    noise = np.random.normal(scale=3, size=x.size)
    y = 10 * np.sin(np.deg2rad(2 * x)) + noise

    # Plot data
    ax.plot(x, y+10, linestyle='-', color='green', linewidth=0.8)

    ax.plot(x, y-10, linestyle='-', color='blue', linewidth=0.8)

    # Save the figure to a file with extra padding around the image
    plt.savefig(filename, dpi=300, pad_inches=0.5)
    plt.close()