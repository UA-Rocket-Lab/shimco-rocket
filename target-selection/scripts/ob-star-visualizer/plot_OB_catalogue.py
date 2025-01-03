"""
Author: Cole Meyer

Description:
This Dash application visualizes distributions of OB-type stars on a galactic map using data from a specified CSV file. Users can interact with the map, select stars, and download their details as a CSV file.
If running locally, run the following in the command line: "python plot_OB_catalogue.py --local True"
"""

import io
import os

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colormaps as cm
import plotly.express as px
import plotly.graph_objs as go
from astropy.modeling import models, fitting
from dash import Dash, dcc, html, Input, Output, State

# ==================================================
# Constants and Data Loading
# ==================================================

STAR_DATA_FILE = "../../ob_catalogue/ob_catalogue.csv"
SPECTRA_DIR = "../../ob_catalogue/ob_catalogue_spectra/"

scale_spectra = True

model_shape = (180, 360) # (lat, lon)
arr = np.sin(np.linspace(-np.pi, np.pi, model_shape[0]).reshape(-1, 1)) * \
    np.cos(np.linspace(-np.pi, np.pi, model_shape[1]))

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Plot OB stars and their corresponding IUE spectra.")
parser.add_argument('--local', type=bool, help='Running locally?', default=False)
args = parser.parse_args()

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
def create_scatter_figure(dataframe):
    """Create the main scatter-geo figure for the star map."""

    fig = go.Figure()

    fig.update_layout(
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor='white',  # Set plot background to white
        paper_bgcolor='white'  # Set outer background to white
    )

    scatter_fig = px.scatter(
        dataframe,
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
        updatemenus=[
            {
                "buttons": [
                    {"label": "O- and B-type", "method": "update", "args": [{"visible": [True, True, True]}]},
                    {"label": "O-type Only", "method": "update", "args": [{"visible": [True, False, False]}]},
                    {"label": "B-type Only", "method": "update", "args": [{"visible": [False, True, False]}]}
                ],
                "direction": "down",
                "x": 1.05,
                "y": 0.8,
                "xanchor": "left",
                "yanchor": "top",
                "font": {"size": 16}
            }
        ]
    )

    fig.update_xaxes(title="Galactic Longitude (°)",range=[0, 360],ticklabelposition="outside top",side="top",showgrid=False)
    fig.update_yaxes(title="Galactic Latitude (°)",range=[-90, 90],showgrid=False)

    return fig

# Initial figure
main_figure = create_scatter_figure(plot_data)

# ==================================================
# Dash Application Initialization
# ==================================================
app = Dash(__name__)

# ==================================================
# Layout
# ==================================================

app.layout = html.Div([
    dcc.Store(id="stored-n-clicks", data=0),
    dcc.Graph(
        id='scatter-plot',
        figure=main_figure,
        config={'scrollZoom': True, 'displayModeBar': True}
    ),
    dcc.Graph(
        id='bottom-right-plot',
        style={
            'position': 'absolute',
            'bottom': '125px',
            'right': '15px',
            'width': '33%',
            'height': '35%',
            'border': '1px solid black',
            'backgroundColor': 'white'
        },
        config={'displayModeBar': False},
        figure={
            'data': [],
            'layout': {
                'xaxis': {'visible': True},
                'yaxis': {'visible': True},
                'title': 'Click on a star to see its data'
            }
        }
    ),
    html.Div(
        [
            html.Label(
                "Available Spectra:",
                style={'fontFamily': 'Arial', 'fontSize': '20px', 'color': '#414141', 'margin-right': '10px'}
            ),
            dcc.Checklist(
                id='show-spectra-checkbox',
                options=[{'label': '', 'value': 'show'}],
                value=[],
                style={'display': 'inline-block'}
            )
        ],
        style={
            'position': 'absolute',
            'top': '122px',
            'right': '55px',
            'display': 'inline-flex',
            'alignItems': 'center'
        }
    ),
    html.Div(
        [
            html.Label(
                "Background:",
                style={'fontFamily': 'Arial', 'fontSize': '20px', 'color': '#414141', 'margin-right': '10px'}
            ),
            dcc.Checklist(
                id='show-bg-checkbox',
                options=[{'label': '', 'value': 'show_bg'}],
                value=[],
                style={'display': 'inline-block'}
            )
        ],
        style={
            'position': 'absolute',
            'top': '155px',
            'right': '55px',
            'display': 'inline-flex',
            'alignItems': 'center'
        }
    ),
    html.Div(
        [
            html.Label(
                "Normalize Spectra:",
                style={'fontFamily': 'Arial', 'fontSize': '20px', 'color': '#414141', 'margin-right': '10px'}
            ),
            dcc.Checklist(
                id='norm-spectra-checkbox',
                options=[{'label': '', 'value': 'norm_spectra'}],
                value=[],
                style={'display': 'inline-block'}
            )
        ],
        style={
            'position': 'absolute',
            'top': '188px',
            'right': '55px',
            'display': 'inline-flex',
            'alignItems': 'center'
        }
    ),
    html.Div(
        [
            html.Label(
                "Show Continuum Fit:",
                style={'fontFamily': 'Arial', 'fontSize': '20px', 'color': '#414141', 'margin-right': '10px'}
            ),
            dcc.Checklist(
                id='show-cont-checkbox',
                options=[{'label': '', 'value': 'show_cont'}],
                value=[],
                style={'display': 'inline-block'}
            )
        ],
        style={
            'position': 'absolute',
            'top': '221px',
            'right': '55px',
            'display': 'inline-flex',
            'alignItems': 'center'
        }
    ),
    html.Div(
        id='clicked-star-info',
        style={
            'position': 'absolute',
            'bottom': '25px',
            'right': '150px',
            'width': '20%',
            'height': '8%',
            'padding': '10px',
            'backgroundColor': 'white',
            'fontSize': '14px',
            'fontFamily': 'Arial'
        },
        children="Click on a star to see details here."
    ),
    html.Div(
        id='selected-stars',
        style={
            'border': '1px solid black', 'padding': '0px', 'overflowY': 'scroll',
            'height': '165px', 'width': '885px', 'position': 'absolute', 'bottom': '15px',
            'right': '535px', 'backgroundColor': 'white'
        }
    ),
    html.Button("Download CSV", id="download-btn", style={
        "position": "absolute", "bottom": "190px", "right": "1270px",
        "fontSize": "18px", "width": "150px", "height": "40px"
    }),
    dcc.Download(id="download-csv")
])

# ==================================================
# Callbacks
# ==================================================

@app.callback(
    [Output("download-csv", "data"), 
     Output("selected-stars", "children"),
     Output("stored-n-clicks", "data")],
    [Input("download-btn", "n_clicks"), Input('scatter-plot', 'selectedData')],
    [State("stored-n-clicks", "data")],
    prevent_initial_call=True
)
def download_csv_and_update_textbox(n_clicks, selected_data, stored_n_clicks):
    """Download the selected stars' data as CSV and update the text area with selected stars."""
    if selected_data is None:
        return None, "Select stars using box select.", stored_n_clicks

    points = selected_data['points']
    star_entries = [
        (
            p['customdata'][0],  # Main_ID
            p['customdata'][1],  # Spectral_Type
            p['customdata'][2],  # m_V
            p['y'],            # GAL_LAT
            p['x']             # GAL_LON
        ) for p in points
    ]

    if star_entries:
        star_entries.insert(0, ('MAIN_ID:', 'SP_TYPE:', 'm_V:', 'GAL_LAT:', 'GAL_LON:'))

    html_vals = []
    for row in star_entries:
        strings = []
        spacings = [35, 14, 12, 27, 0]
        for j in range(len(row)):
            strings.append(str(row[j])+(spacings[j]-len(str(row[j])))*' ')

        html_vals.append(html.Span(f"{strings[0]}{strings[1]}{strings[2]}{strings[3]}{strings[4]}\n"))

    formatted_text = html.Div(
        html_vals,
        style={"whiteSpace": "pre-wrap", "fontFamily": "monospace"}
    )

    # Only trigger download if button was clicked
    if n_clicks and n_clicks > stored_n_clicks:
        buffer = io.StringIO()
        np.savetxt(buffer, np.array(star_entries[1:], dtype=str), delimiter=",", fmt="%s")
        csv_content = buffer.getvalue()
        buffer.close()

        return {
            "content": csv_content,
            "filename": "selected_stars.csv",
            "type": "text/csv"
        }, formatted_text, n_clicks

    # Otherwise, just update the text box
    return None, formatted_text, stored_n_clicks


@app.callback(
    Output('bottom-right-plot', 'figure'),
    [Input('scatter-plot', 'clickData'),
    Input('norm-spectra-checkbox', 'value'),
    Input('show-cont-checkbox', 'value')]
)
def update_bottom_right_plot(clicked_data, norm_spectra_value, show_cont_value):
    """Update the bottom-right plot to show star spectra when a star is clicked."""

    # Logic for readability
    showing_spectrum = False
    show_spectrum = clicked_data and 'points' in clicked_data and 'customdata' in clicked_data['points'][0].keys()
    norm_spectrum = len(norm_spectra_value) != 0
    show_continuum = len(show_cont_value) != 0

    # Plotting code
    if norm_spectrum and show_spectrum:

        point = clicked_data['points'][0]
        star_name = point['customdata'][0]

        # Format star name to match spectra files
        star_filename = star_name.replace(' ', '_')
        files = os.listdir(SPECTRA_DIR)
        
        if f"{star_filename}.csv" in files:

            showing_spectrum = True

            star_spectrum = np.genfromtxt(f"{SPECTRA_DIR}{star_filename}.csv", delimiter=',', dtype='float')
            if star_spectrum.ndim == 2:
                half = int(star_spectrum.shape[1]/2)
            else:
                half = int(star_spectrum.shape[0]/2)

            if star_spectrum.ndim == 2:
                mean_val = np.mean(star_spectrum[:, half:])
                for i in range(star_spectrum.shape[0]):
                    star_spectrum[i, half:] *= mean_val / np.mean(star_spectrum[i, half:])

            y_min = np.min(star_spectrum[:, half:] if star_spectrum.ndim == 2 else star_spectrum[half:])
            y_max = np.max(star_spectrum[:, half:] if star_spectrum.ndim == 2 else star_spectrum[half:])
            shaded_regions = [
                go.Scatter(
                    x=[1395, 1405, 1405, 1395],
                    y=[y_min, y_min, y_max, y_max],
                    fill='toself',
                    mode='none',
                    showlegend=False,
                    fillcolor='rgba(255, 200, 200, 0.5)'
                ),
                go.Scatter(
                    x=[1605, 1615, 1615, 1605],
                    y=[y_min, y_min, y_max, y_max],
                    fill='toself',
                    mode='none',
                    showlegend=False,
                    fillcolor='rgba(200, 200, 255, 0.5)'
                )
            ]

            if star_spectrum.ndim == 2:
                # Multiple rows of data (multiple lines)
                traces = [
                    go.Scatter(
                        x=star_spectrum[i, :half],
                        y=star_spectrum[i, half:],
                        mode='lines',
                        line_color='black',
                        line_width=2,
                        showlegend=False
                    ) for i in range(star_spectrum.shape[0])
                ]
            else:
                # Single line of data
                traces = [
                    go.Scatter(
                        x=star_spectrum[:half],
                        y=star_spectrum[half:],
                        mode='lines',
                        line_color='black',
                        line_width=2,
                        showlegend=False
                    )
                ]

            figure = {
                'data': traces + shaded_regions,
                'layout': {
                    'xaxis': {'title': 'Wavelength (Å)'},
                    'yaxis': {'showticklabels': False},
                    'margin': {'l': 10, 'r': 10, 't': 35, 'b': 35},
                    'title': f'Star: {star_name}'
                }
            }

    elif show_spectrum:

        point = clicked_data['points'][0]
        star_name = point['customdata'][0]

        # Format star name to match spectra files
        star_filename = star_name.replace(' ', '_')
        files = os.listdir(SPECTRA_DIR)
        
        if f"{star_filename}.csv" in files:

            showing_spectrum = True

            star_spectrum = np.genfromtxt(f"{SPECTRA_DIR}{star_filename}.csv", delimiter=',', dtype='float')
            if star_spectrum.ndim == 2:
                half = int(star_spectrum.shape[1]/2)
            else:
                half = int(star_spectrum.shape[0]/2)

            y_min = np.min(star_spectrum[:, half:] if star_spectrum.ndim == 2 else star_spectrum[half:])
            y_max = np.max(star_spectrum[:, half:] if star_spectrum.ndim == 2 else star_spectrum[half:])
            shaded_regions = [
                go.Scatter(
                    x=[1395, 1405, 1405, 1395],
                    y=[y_min, y_min, y_max, y_max],
                    fill='toself',
                    mode='none',
                    showlegend=False,
                    fillcolor='rgba(255, 200, 200, 0.5)'
                ),
                go.Scatter(
                    x=[1605, 1615, 1615, 1605],
                    y=[y_min, y_min, y_max, y_max],
                    fill='toself',
                    mode='none',
                    showlegend=False,
                    fillcolor='rgba(200, 200, 255, 0.5)'
                )
            ]

            if star_spectrum.ndim == 2:
                # Multiple rows of data (multiple lines)
                traces = [
                    go.Scatter(
                        x=star_spectrum[i, :half],
                        y=star_spectrum[i, half:],
                        mode='lines',
                        line_color='black',
                        line_width=2,
                        showlegend=False
                    ) for i in range(star_spectrum.shape[0])
                ]
            else:
                # Single line of data
                traces = [
                    go.Scatter(
                        x=star_spectrum[:half],
                        y=star_spectrum[half:],
                        mode='lines',
                        line_color='black',
                        line_width=2,
                        showlegend=False
                    )
                ]

            figure = {
                'data': traces + shaded_regions,
                'layout': {
                    'xaxis': {'title': 'Wavelength (Å)'},
                    'yaxis': {'showticklabels': False},
                    'margin': {'l': 10, 'r': 10, 't': 35, 'b': 35},
                    'title': f'Star: {star_name}'
                }
            }

    if show_continuum and showing_spectrum:

        masked_regions = ['1150:1265','1375:1425','1515:1675']
        unmasked_regions = ['0:1150','1265:1375','1425:1515','1675:2000']
        unmasked_regions = ['1325:2000']

        if star_spectrum.ndim == 2:
            avg_wav = np.mean(star_spectrum[:, :half], axis=0)
            avg_flux = np.mean(star_spectrum[:, half:], axis=0)
        else:
            avg_wav = star_spectrum[:half]
            avg_flux = star_spectrum[half:]

        mask = np.ones_like(avg_wav).astype('bool')
        for region in masked_regions:
            lims = np.array(region.split(':')).astype('float')
            mask *= np.invert((lims[0]<avg_wav)&(avg_wav<lims[1]))

        poly_init = models.Chebyshev1D(degree=3)
        fitter = fitting.LinearLSQFitter()
        cont_model = fitter(poly_init, avg_wav[mask], avg_flux[mask])
        cont_flux = cont_model(avg_wav)
        normalized_flux = avg_flux/cont_flux

        traces.append(
            go.Scatter(
                x=avg_wav,
                y=avg_flux,
                mode='lines',
                line_color='red',
                line_width=2,
                showlegend=False
            )
        )
        traces.append(
            go.Scatter(
                x=avg_wav,
                y=cont_flux,
                mode='lines',
                line_color='blue',
                line_dash='longdash',
                line_width=2,
                showlegend=False
            )
        )

    if showing_spectrum:

        figure = {
            'data': traces + shaded_regions,
            'layout': {
                'xaxis': {'title': 'Wavelength (Å)'},
                'yaxis': {'showticklabels': False},
                'margin': {'l': 10, 'r': 10, 't': 35, 'b': 35},
                'title': f'Star: {star_name}'
            }
        }

        return figure
    else:
        # Default empty figure if no star is clicked yet
        return {
            'data': [],
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'margin': {'l': 10, 'r': 10, 't': 35, 'b': 35},
                'title': 'Click on a star to see its data'
            }
        }

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('show-spectra-checkbox', 'value'),
     Input('show-bg-checkbox', 'value')]
)
def update_scatter_plot_and_bg(show_spectra_value, show_bg_value):
    """Update the scatter plot to filter stars and toggle background visibility."""
    # Filter stars based on "Show Available Spectra"
    if 'show' in show_spectra_value:
        filtered_data = plot_data[plot_data['Name'].isin(spectra_star_names)]
    else:
        filtered_data = plot_data

    fig = go.Figure()
    if 'show_bg' in show_bg_value:
        lons = np.linspace(0, 360, arr.shape[1])
        lats = np.linspace(-90, 90, arr.shape[0])
        fig.add_trace(go.Heatmap(
            x=lons,
            y=lats,
            z=arr,
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

    # Add scatter plot data
    scatter_fig = px.scatter(
        filtered_data,
        x="Galactic Longitude",
        y="Galactic Latitude",
        color="Color",
        size="Size",
        custom_data=["Name", "Spectral Type", "Apparent Magnitude"],
        color_discrete_map=color_map
    )
    for trace in scatter_fig.data:
        fig.add_trace(trace)

    for lat_line in range(-90, 91, 30):
        fig.add_shape(type='line', xref='x', yref='y',
                    x0=0, x1=360, y0=lat_line, y1=lat_line,
                    line=dict(color='gray', width=0.5))
    for lon_line in range(0, 361, 30):
        fig.add_shape(type='line', xref='x', yref='y',
                    x0=lon_line, x1=lon_line, y0=-90, y1=90,
                    line=dict(color='gray', width=0.5))

    # Update figure layout
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
    fig.update_xaxes(title="Galactic Longitude (°)", range=[0, 360], ticklabelposition="outside top", side="top", showgrid=False)
    fig.update_yaxes(title="Galactic Latitude (°)", range=[-90, 90], showgrid=False)
    fig.update_layout(
        title="SiMBAD OB Stars Visualizer",
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend_title=dict(text="Spectral Type"),
        legend=dict(font=dict(size=20), x=1.03, y=1, xanchor="left", yanchor="top"),
        autosize=False,
        width=1175,
        height=650
    )

    return fig


@app.callback(
    Output('clicked-star-info', 'children'),
    Input('scatter-plot', 'clickData')
)
def update_clicked_star_info(clicked_data):
    """Update the info panel with details of the clicked star."""
    if clicked_data and 'points' in clicked_data and 'customdata' in clicked_data['points'][0].keys():
        point = clicked_data['points'][0]
        sp_type = point['customdata'][1]
        m_v = point['customdata'][2]
        gal_lat = point['y']
        gal_lon = point['x']
        return html.Div(
            style={
                'display': 'grid',
                'gridTemplateColumns': '1fr 1fr',
                'gap': '10px',
                'textAlign': 'left'
            },
            children=[
                html.Div([
                    html.P(f"SP_TYPE:   {sp_type}"),
                    html.P(f"m_V:       {m_v:.2f}")
                ]),
                html.Div([
                    html.P(f"GAL_LAT:   {gal_lat:.4f}"),
                    html.P(f"GAL_LON:   {gal_lon:.4f}")
                ])
            ]
        )
    return "Click on a star to see details here."

# ==================================================
# Main
# ==================================================
if not args.local:
    port = int(os.environ.get("PORT", 8050))

if __name__ == '__main__':

    if args.local:
        app.run_server(debug=True)
    else:
        app.run_server(host='0.0.0.0', port=port, debug=True)
