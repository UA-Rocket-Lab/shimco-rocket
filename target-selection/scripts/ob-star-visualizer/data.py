import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# ==================================================
# Constants and Data Loading
# ==================================================

STAR_DATA_FILE = "../../ob_catalogue/ob_catalogue.csv"
SPECTRA_DIR = "../../ob_catalogue/ob_catalogue_spectra/"

# Generate model
# model_shape = (180, 360) # (lat, lon)
# model_data = np.sin(np.linspace(-np.pi, np.pi, model_shape[0]).reshape(-1, 1)) * \
#     np.cos(np.linspace(-np.pi, np.pi, model_shape[1]))
model_data = np.genfromtxt('../../bp_integrated_h2.csv', delimiter=',', dtype='float')

# Load star data (Main_ID, m_V, GAL_LON, GAL_LAT, SP_TYPE)
raw_stars = np.genfromtxt(STAR_DATA_FILE, delimiter=',', dtype='str')
spectra_files = os.listdir(SPECTRA_DIR)
spectra_star_names = [file.split('.')[0].replace('_', ' ') for file in spectra_files]

# ==================================================
# Data Preparation
# ==================================================

# Assign colors based on spectral type
color_labels = ["O-type" if s.startswith("O") else "B-type" if s.startswith("B") else "Other"
                for s in raw_stars[:, 4]]
color_map = {"O-type": "blue", "B-type": "red", "Other": "gray"}

# Assign sizes in a decreasing sequence as an exponential
pt1 = [np.min(raw_stars[:,1].astype('float')), 100]
pt2 = [np.max(raw_stars[:,1].astype('float')), 1]
tau = (pt2[0]-pt1[0]) / np.log(pt1[1]/pt2[1])
A = pt1[1] * np.exp(pt1[0] / tau)
sizes = A * np.exp(-raw_stars[:,1].astype('float') / tau)

# Create a DataFrame for plotting
plot_data = pd.DataFrame({
    "Name": raw_stars[:, 0],
    "Apparent Magnitude": raw_stars[:, 1].astype(float),
    "Galactic Longitude": raw_stars[:, 2].astype(float),
    "Galactic Latitude": raw_stars[:, 3].astype(float),
    "Spectral Type": raw_stars[:, 4],
    "Color": color_labels,
    "Size": sizes
})
nighttime_frac = np.column_stack((raw_stars[:,0],raw_stars[:,8:]))

# Custom hover text
plot_data["Hover Text"] = plot_data.apply(
    lambda row: (
        f"Main_ID: {row['Name']}<br>SP_TYPE: {row['Spectral Type']}<br>m_V: {row['Apparent Magnitude']}"
        f"<br>GAL_LAT: {row['Galactic Latitude']:.4f}<br>GAL_LON: {row['Galactic Longitude']:.4f}"
    ), axis=1
)

# ==================================================
# Figure Creation
# ==================================================

def scatter_fig(show_spectra=[], show_bg=[], xlims=[0,360], ylims=[-90,90]):
    
    fig = go.Figure()

    if show_bg == [True]:
        lons = np.linspace(0, 360, model_data.shape[1])
        lats = np.linspace(-90, 90, model_data.shape[0])
        fig.add_trace(go.Heatmap(
            x=lons,
            y=lats,
            z=model_data,
            zmin=0,
            zmax=5e5,
            colorscale='Viridis',
            colorbar=dict(
                orientation='h',
                x=0.59,
                xanchor='center',
                y=-0.15,
                ticklabelposition='outside bottom',
                title=dict(
                    text=r"H2 Integrated Emission (erg / s / cm^2 / arcsec^2)",
                    side="bottom"
                ),
                len=0.5,
                thickness=15
            ),
            hovertemplate='GAL_LAT: %{y}<br>GAL_LON: %{x}<br>Value: %{z}<extra></extra>'
        ))

    if show_spectra == [True]:
        scatter_fig = px.scatter(
            plot_data[plot_data['Name'].isin(spectra_star_names)],
            x="Galactic Longitude",
            y="Galactic Latitude",
            color="Color",
            size="Size",
            custom_data=["Name", "Spectral Type", "Apparent Magnitude"],
            color_discrete_map=color_map
        )
    else:
        scatter_fig = px.scatter(
            plot_data,
            x="Galactic Longitude",
            y="Galactic Latitude",
            color="Color",
            size="Size",
            custom_data=["Name", "Spectral Type", "Apparent Magnitude"],
            color_discrete_map=color_map
        )

    for trace in scatter_fig.data:
        fig.add_trace(trace)

    fig.update_traces(
        marker=dict(line=dict(width=0)),
        hovertemplate=(
            "Main_ID: %{customdata[0]}<br>"
            "SP_TYPE: %{customdata[1]}<br>"
            "m_V: %{customdata[2]:.2f}<br>"
            "GAL_LAT: %{y:.4f}<br>"
            "GAL_LON: %{x:.4f}<extra></extra>"
        ),
        selector=dict(type='scatter')
    )

    # Plot lat/lon grid
    for lat_line in range(-90, 91, 30):
        fig.add_shape(type='line', xref='x', yref='y',
                    x0=0, x1=360, y0=lat_line, y1=lat_line,
                    line=dict(color='gray', width=0.5))
    for lon_line in range(0, 361, 30):
        fig.add_shape(type='line', xref='x', yref='y',
                    x0=lon_line, x1=lon_line, y0=-90, y1=90,
                    line=dict(color='gray', width=0.5))

    fig.update_layout(
        title="SiMBAD OB Stars Visualizer",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend_title=dict(text="Spectral Type"),
        legend=dict(
            font=dict(size=20),
            x=1.03,
            y=1,
            xanchor="left",
            yanchor="top"
        ),
        autosize=False,
        width=1175,
        height=650,
    )

    fig.update_xaxes(title="Galactic Longitude (°)", range=xlims, ticklabelposition="outside top", side="top", showgrid=False)
    fig.update_yaxes(title="Galactic Latitude (°)", range=ylims, showgrid=False)

    return fig

# Create the initial figure
main_fig = scatter_fig()