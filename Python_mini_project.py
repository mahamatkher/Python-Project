import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors
import colorsys

# === Main Window ===
root = tk.Tk()
root.title("Data Visualization Tool")
root.geometry("800x600")
root.minsize(700, 500)

# Center the window on screen
root.eval('tk::PlaceWindow . center')

# === Main Container ===
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

# === Title ===
ttk.Label(main_frame, text="📊 Data Visualization Tool", 
        font=("Arial", 16, "bold")).pack(pady=(0, 15))

# === Input Frame ===
input_frame = ttk.Frame(main_frame)
input_frame.pack(fill="x", pady=5)

ttk.Label(input_frame, text="Categories (comma-separated):").grid(row=0, column=0, sticky="w", pady=2)
subjects_var = tk.StringVar(value="Math, Science, English, History, Art, Geography")
ttk.Entry(input_frame, textvariable=subjects_var, width=60).grid(row=0, column=1, padx=5, pady=2)

ttk.Label(input_frame, text="Values (comma-separated):").grid(row=1, column=0, sticky="w", pady=2)
scores_var = tk.StringVar(value="85, 92, 78, 88, 95, 82")
ttk.Entry(input_frame, textvariable=scores_var, width=60).grid(row=1, column=1, padx=5, pady=2)

# === Controls Frame ===
controls_frame = ttk.Frame(main_frame)
controls_frame.pack(fill="x", pady=10)

ttk.Label(controls_frame, text="Chart Type:").grid(row=0, column=0, padx=5)
chart_type = tk.StringVar(value="Bar")
chart_combo = ttk.Combobox(controls_frame, textvariable=chart_type, width=15,
                        values=["Bar", "Line", "Scatter", "Histogram", "Pie", "Boxplot", "Area", "Stem"])
chart_combo.grid(row=0, column=1, padx=5)

ttk.Label(controls_frame, text="Color:").grid(row=0, column=2, padx=5)
color_var = tk.StringVar(value="royalblue")
color_combo = ttk.Combobox(controls_frame, textvariable=color_var, width=12,
                        values=["royalblue","green","red","orange","purple","gold","skyblue","pink",
                                "teal","coral","navy","maroon","olive","brown"])
color_combo.grid(row=0, column=3, padx=5)

# Function to generate color variations for pie chart
def generate_pie_colors(base_color, n_colors):
    """Generate different shades of the base color for pie chart slices"""
    try:
        # Convert to RGB then to HSL for better color manipulation
        base_rgb = mcolors.to_rgb(base_color)
        base_hls = colorsys.rgb_to_hls(*base_rgb)
        
        colors = []
        for i in range(n_colors):
            # Vary the lightness to create different shades
            # This creates a nice gradient from lighter to darker
            lightness = 0.3 + (0.5 * i / max(1, n_colors-1))
            
            # Keep hue and saturation mostly the same, just adjust lightness
            new_hls = (
                base_hls[0],  # Keep same hue
                max(0.1, min(0.9, lightness)),  # Vary lightness
                base_hls[2]   # Keep same saturation
            )
            
            # Convert back to RGB
            new_rgb = colorsys.hls_to_rgb(*new_hls)
            colors.append(new_rgb)
        
        return colors
    except:
        # Fallback: use matplotlib's built-in color variations
        base_rgb = mcolors.to_rgb(base_color)
        colors = []
        for i in range(n_colors):
            factor = 0.4 + (0.6 * i / max(1, n_colors-1))
            new_color = tuple(min(1.0, c * factor) for c in base_rgb)
            colors.append(new_color)
        return colors

# === Analyze Button ===
def analyze_data():
    # Clear previous plot
    for widget in plot_frame.winfo_children():
        widget.destroy()
    
    # Get and validate input
    subjects_input = subjects_var.get().strip()
    scores_input = scores_var.get().strip()
    
    if not scores_input:
        messagebox.showerror("Error", "Please enter numeric values.")
        return
    
    subjects = [s.strip() for s in subjects_input.split(",") if s.strip()]
    score_values = [s.strip() for s in scores_input.split(",") if s.strip()]
    
    try:
        scores = [float(x) for x in score_values]
    except ValueError:
        messagebox.showerror("Error", "Values must be numbers.")
        return
    
    if not subjects:
        subjects = [f"Item {i+1}" for i in range(len(scores))]
    
    # Validate data length
    chart = chart_type.get()
    if len(subjects) != len(scores) and chart not in ["Histogram", "Boxplot"]:
        messagebox.showerror("Error", "Number of categories and values must match.")
        return
    
    # Calculate statistics
    data = np.array(scores)
    stats_text = (f"Mean: {np.mean(data):.2f} | Median: {np.median(data):.2f} | "
                f"Std Dev: {np.std(data):.2f} | Min: {np.min(data):.2f} | Max: {np.max(data):.2f}")
    ttk.Label(plot_frame, text=stats_text, font=("Arial", 10)).pack(pady=5)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(8, 5))
    x_pos = np.arange(len(subjects))
    
    try:
        chosen_color = color_var.get()
        
        if chart == "Bar":
            ax.bar(x_pos, scores, color=chosen_color)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(subjects, rotation=45, ha='right')
        elif chart == "Line":
            ax.plot(x_pos, scores, color=chosen_color, marker="o", linewidth=2)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(subjects, rotation=45, ha='right')
        elif chart == "Scatter":
            ax.scatter(x_pos, scores, color=chosen_color, s=80)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(subjects, rotation=45, ha='right')
        elif chart == "Histogram":
            ax.hist(scores, bins='auto', color=chosen_color, edgecolor="black")
        elif chart == "Pie":
            # FIXED: Generate different shades of the chosen color
            colors = generate_pie_colors(chosen_color, len(scores))
            ax.pie(scores, labels=subjects, autopct="%1.1f%%", startangle=90, colors=colors)
        elif chart == "Boxplot":
            ax.boxplot(scores, patch_artist=True, 
                    boxprops=dict(facecolor=chosen_color))
        elif chart == "Area":
            ax.fill_between(x_pos, scores, color=chosen_color, alpha=0.5)
            ax.plot(x_pos, scores, color=chosen_color)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(subjects, rotation=45, ha='right')
        elif chart == "Stem":
            markerline, stemlines, baseline = ax.stem(x_pos, scores, basefmt=" ")
            plt.setp(markerline, color=chosen_color, markersize=8)
            plt.setp(stemlines, color=chosen_color)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(subjects, rotation=45, ha='right')
        
        ax.set_title(f"{chart} Chart")
        if chart != "Pie":
            ax.set_xlabel("Categories")
            ax.set_ylabel("Values")
            ax.grid(True, linestyle="--", alpha=0.6)
        
        fig.tight_layout()
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, plot_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=5)
        canvas.draw()
        
    except Exception as e:
        plt.close(fig)
        messagebox.showerror("Plot Error", str(e))

ttk.Button(main_frame, text="Analyze & Visualize", command=analyze_data).pack(pady=10)

# === Plot Frame ===
plot_frame = ttk.Frame(main_frame)
plot_frame.pack(fill="both", expand=True, pady=10)

# Start with sample data
analyze_data()

root.mainloop()