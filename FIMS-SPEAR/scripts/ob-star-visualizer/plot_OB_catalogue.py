"""
Author: Cole Meyer

Description:
This Dash application visualizes distributions of OB-type stars on a galactic map using data from a specified CSV file.
Users can interact with the map, select stars, and download their details as a CSV file.
"""

import io
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output

# ==================================================
# Constants and Data Loading
# ==================================================

STAR_DATA_FILE = "../../ob_catalogue/ob_catalogue.csv"
SPECTRA_DIR = "../../ob_catalogue/ob_catalogue_spectra/"

# Load star data (Main_ID, m_V, GAL_LON, GAL_LAT, SP_TYPE)
raw_stars = np.genfromtxt(STAR_DATA_FILE, delimiter=',', dtype='str')
spectra_files = os.listdir(SPECTRA_DIR)
spectra_star_names = [file.split('.')[0].replace('_', ' ') for file in spectra_files]

# A sample data file is loaded for determining dimensions needed for later plot operations
sample_data = pd.read_csv(f"{SPECTRA_DIR}BD+44_1148.csv", header=None).values.astype(float)

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
    fig = px.scatter_geo(
        dataframe,
        lon="Galactic Longitude",
        lat="Galactic Latitude",
        color="Color",
        size="Size",
        custom_data=["Name", "Spectral Type", "Apparent Magnitude"],
        projection="aitoff",
        title="SiMBAD OB Star Distribution",
        color_discrete_map=color_map
    )

    fig.update_geos(
        showland=False, showcountries=False, showcoastlines=False, showocean=False, showframe=False,
        projection_scale=1,
        lonaxis=dict(showgrid=True, gridcolor="lightgray", dtick=30),
        lataxis=dict(showgrid=True, gridcolor="lightgray", dtick=30),
        domain=dict(x=[0, 1], y=[0.2, 1])
    )

    fig.update_traces(marker=dict(sizemode='diameter', sizeref=2.5, sizemin=3))

    fig.update_traces(
        marker=dict(line=dict(width=0)),
        hovertemplate=(
            "Main_ID: %{customdata[0]}<br>"
            "SP_TYPE: %{customdata[1]}<br>"
            "m_V: %{customdata[2]:.2f}<br>"
            "GAL_LAT: %{lat:.4f}<br>"
            "GAL_LON: %{lon:.4f}<extra></extra>"
        )
    )

    fig.update_layout(
        legend_title=dict(text="Spectral Type"),
        legend=dict(
            font=dict(size=20),
            x=1.03,
            y=1,
            xanchor="left",
            yanchor="top"
        ),
        autosize=False,
        width=1200,
        height=800,
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
                "Show Available Spectra:",
                style={'fontSize': '20px', 'margin-right': '10px'}
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
            'top': '237px',
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
    [Output("download-csv", "data"), Output("selected-stars", "children")],
    [Input("download-btn", "n_clicks"), Input('scatter-plot', 'selectedData')],
    prevent_initial_call=True
)
def download_csv_and_update_textbox(n_clicks, selected_data):
    """Download the selected stars' data as CSV and update the text area with selected stars."""
    if selected_data is None:
        return None, "Select stars using box select."

    points = selected_data['points']
    star_entries = [
        (
            p['customdata'][0],  # Main_ID
            p['customdata'][1],  # Spectral_Type
            p['customdata'][2],  # m_V
            p['lat'],            # GAL_LAT
            p['lon']             # GAL_LON
        ) for p in points
    ]

    if star_entries:
        star_entries.insert(0, ('MAIN_ID:', 'SP_TYPE:', 'm_V:', 'GAL_LAT:', 'GAL_LON:'))

    formatted_text = html.Div(
        [html.Span(f"{row[0]:<25}{row[1]:>10}{row[2]:>18}{row[3]:>30}{row[4]:>30}\n") for row in star_entries],
        style={"whiteSpace": "pre-wrap", "fontFamily": "monospace"}
    )

    # If the download button is not clicked yet, just update the text
    if not n_clicks:
        return None, formatted_text

    # If the download button is clicked, provide the CSV download
    buffer = io.StringIO()
    np.savetxt(buffer, np.array(star_entries[1:], dtype=str), delimiter=",", fmt="%s")
    csv_content = buffer.getvalue()
    buffer.close()

    return {
        "content": csv_content,
        "filename": "selected_stars.csv",
        "type": "text/csv"
    }, formatted_text


@app.callback(
    Output('bottom-right-plot', 'figure'),
    [Input('scatter-plot', 'clickData')]
)
def update_bottom_right_plot(clicked_data):
    """Update the bottom-right plot to show star spectra when a star is clicked."""
    if clicked_data and 'points' in clicked_data:
        point = clicked_data['points'][0]
        star_name = point['customdata'][0]

        # Format star name to match spectra files
        star_filename = star_name.replace(' ', '_')
        files = os.listdir(SPECTRA_DIR)
        
        if f"{star_filename}.csv" in files:
            star_spectrum = np.genfromtxt(f"{SPECTRA_DIR}{star_filename}.csv", delimiter=',', dtype='float')
            half = int(sample_data.shape[1]/2)
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
            return figure
        else:
            # No spectrum available
            return {
                'data': [],
                'layout': {
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False},
                    'margin': {'l': 10, 'r': 10, 't': 35, 'b': 35},
                    'title': f'Star: {star_name} (no spectrum available)'
                }
            }

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
    Input('show-spectra-checkbox', 'value')
)
def update_scatter_plot(show_spectra_value):
    """Update the main scatter plot to filter stars that have available spectra if checkbox is selected."""
    if 'show' in show_spectra_value:
        filtered_data = plot_data[plot_data['Name'].isin(spectra_star_names)]
    else:
        filtered_data = plot_data

    updated_fig = create_scatter_figure(filtered_data)
    return updated_fig


@app.callback(
    Output('clicked-star-info', 'children'),
    Input('scatter-plot', 'clickData')
)
def update_clicked_star_info(clicked_data):
    """Update the info panel with details of the clicked star."""
    if clicked_data and 'points' in clicked_data:
        point = clicked_data['points'][0]
        sp_type = point['customdata'][1]
        m_v = point['customdata'][2]
        gal_lat = point['lat']
        gal_lon = point['lon']
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

port = int(os.environ.get("PORT", 8050))

# ==================================================
# Main
# ==================================================
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=port, debug=True)
