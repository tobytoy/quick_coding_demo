import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
import time

# Set up the Streamlit app layout
st.set_page_config(layout="wide")
st.title("Epicycle Reconstruction from Handwriting")

# Sidebar controls
st.sidebar.header("Controls")
num_circles = st.sidebar.slider("Number of Epicycles", min_value=1, max_value=50, value=10)
speed = st.sidebar.slider("Animation Speed", min_value=1, max_value=10, value=5)
show_circles = st.sidebar.checkbox("Show Circles", value=True)
show_path = st.sidebar.checkbox("Show Path", value=True)
start_button = st.sidebar.button("Start Animation")
clear_button = st.sidebar.button("Clear Canvas")

# Initialize session state
if "points" not in st.session_state or clear_button:
    st.session_state.points = []
    st.session_state.animating = False
    
if start_button:
    st.session_state.animating = True

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Draw Here")
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#ffffff",
        height=500,
        width=500,
        drawing_mode="freedraw",
        key="canvas",
    )

    # Extract points from canvas
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        points = []
        for obj in objects:
            if obj["type"] == "path":
                for seg in obj["path"]:
                    if seg[0] in ["L", "M"]:
                        points.append([seg[1], seg[2]])
        if len(points) > 0:
            st.session_state.points = points

with col2:
    st.subheader("Epicycle Reconstruction")
    plot_placeholder = st.empty()
    
    if st.session_state.animating and len(st.session_state.points) > 10:
        # Convert points to complex numbers
        pts = np.array(st.session_state.points)
        
        # Resample to fixed number of points for smoother animation
        num_points = min(500, len(pts))
        indices = np.linspace(0, len(pts) - 1, num_points).astype(int)
        pts = pts[indices]
        
        # Center the points
        center = np.mean(pts, axis=0)
        pts_centered = pts - center
        
        # Convert to complex numbers (flip y for correct orientation)
        complex_pts = pts_centered[:, 0] - 1j * pts_centered[:, 1]
        
        # Perform Fourier Transform
        N = len(complex_pts)
        fourier_coeffs = fft(complex_pts) / N
        
        # Create frequency array
        freqs = np.arange(N)
        freqs = np.where(freqs > N // 2, freqs - N, freqs)
        
        # Sort by amplitude (magnitude)
        amplitudes = np.abs(fourier_coeffs)
        sorted_indices = np.argsort(-amplitudes)
        
        # Select top circles
        num_circles_to_use = min(num_circles, len(sorted_indices))
        selected_indices = sorted_indices[:num_circles_to_use]
        selected_coeffs = fourier_coeffs[selected_indices]
        selected_freqs = freqs[selected_indices]
        
        # Animation loop
        num_frames = 100
        path_x = []
        path_y = []
        
        for frame in range(num_frames):
            t = 2 * np.pi * frame / num_frames
            
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.set_xlim(-250, 250)
            ax.set_ylim(-250, 250)
            ax.set_aspect('equal')
            ax.set_facecolor('#f0f0f0')
            ax.grid(True, alpha=0.3)
            
            # Calculate epicycle positions
            x, y = 0, 0
            positions = [(x, y)]
            
            for i in range(len(selected_coeffs)):
                coeff = selected_coeffs[i]
                freq = selected_freqs[i]
                
                # Calculate rotation
                radius = np.abs(coeff)
                angle = np.angle(coeff) + freq * t
                
                # New position
                x += radius * np.cos(angle)
                y += radius * np.sin(angle)
                positions.append((x, y))
                
                # Draw circle
                if show_circles:
                    prev_x, prev_y = positions[-2]
                    circle = plt.Circle((prev_x, prev_y), radius, 
                                      fill=False, color='gray', alpha=0.3, linewidth=1)
                    ax.add_patch(circle)
                    
                    # Draw radius line
                    ax.plot([prev_x, x], [prev_y, y], 'b-', linewidth=1, alpha=0.5)
            
            # Add current position to path
            path_x.append(x)
            path_y.append(y)
            
            # Draw the traced path
            if show_path and len(path_x) > 1:
                ax.plot(path_x, path_y, 'r-', linewidth=2, alpha=0.8)
            
            # Draw the final position
            ax.plot(x, y, 'ro', markersize=8)
            
            # Draw original shape in light gray
            original_x = pts_centered[:, 0]
            original_y = -pts_centered[:, 1]
            ax.plot(original_x, original_y, 'k--', linewidth=1, alpha=0.2, label='Original')
            
            ax.set_title(f'Frame {frame + 1}/{num_frames}')
            ax.legend(loc='upper right')
            
            plot_placeholder.pyplot(fig)
            plt.close()
            
            time.sleep(0.01 / speed)
        
        st.session_state.animating = False
        st.rerun()
    
    elif len(st.session_state.points) > 10:
        # Show static preview
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(-250, 250)
        ax.set_ylim(-250, 250)
        ax.set_aspect('equal')
        ax.set_facecolor('#f0f0f0')
        ax.grid(True, alpha=0.3)
        
        pts = np.array(st.session_state.points)
        center = np.mean(pts, axis=0)
        pts_centered = pts - center
        ax.plot(pts_centered[:, 0], -pts_centered[:, 1], 'b-', linewidth=2)
        ax.set_title('Click "Start Animation" to begin')
        
        plot_placeholder.pyplot(fig)
        plt.close()
    else:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(-250, 250)
        ax.set_ylim(-250, 250)
        ax.set_aspect('equal')
        ax.set_facecolor('#f0f0f0')
        ax.text(0, 0, 'Draw something on the left!', 
                ha='center', va='center', fontsize=14)
        plot_placeholder.pyplot(fig)
        plt.close()

# Instructions
st.sidebar.markdown("---")
st.sidebar.markdown("""
### How to use:
1. Draw a shape on the left canvas
2. Adjust the number of epicycles
3. Click "Start Animation" to see the reconstruction
4. Use "Clear Canvas" to start over
""")