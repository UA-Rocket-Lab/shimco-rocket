from dash import Dash, html, dcc
import argparse

from data import main_fig
# from main import args

app = Dash(__name__)

# ==================================================
# Layout
# ==================================================

parser = argparse.ArgumentParser(description="Process the --local flag.")
parser.add_argument(
    '--local',
    action='store_true',
    default=False,
    help='Enable local mode (default: False)'
)
args = parser.parse_args()

def main_layout():
        
    children = [

        ### MAIN SCATTERPLOT
        dcc.Graph(
            id='scatter-plot',
            figure=main_fig,
            config={'scrollZoom': True, 'displayModeBar': True}
        ),

        ### CHECKBOXES
        html.Div(
            [
                html.Label(
                    "Available IUE Spectra:",
                    style={'fontFamily': 'Arial', 'fontSize': '20px', 'color': '#414141', 'margin-right': '10px'}
                ),
                dcc.Checklist(
                    id='show-spectra-checkbox',
                    options=[{'label': '', 'value': True}],
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
                    "BP Integrated H2 Map:",
                    style={'fontFamily': 'Arial', 'fontSize': '20px', 'color': '#414141', 'margin-right': '10px'}
                ),
                dcc.Checklist(
                    id='show-bg-checkbox',
                    options=[{'label': '', 'value': True}],
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
                    "Normalize IUE Spectra:",
                    style={'fontFamily': 'Arial', 'fontSize': '20px', 'color': '#414141', 'margin-right': '10px'}
                ),
                dcc.Checklist(
                    id='norm-spectra-checkbox',
                    options=[{'label': '', 'value': True}],
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
                    "Show IUE Continuum Fit:",
                    style={'fontFamily': 'Arial', 'fontSize': '20px', 'color': '#414141', 'margin-right': '10px'}
                ),
                dcc.Checklist(
                    id='show-cont-checkbox',
                    options=[{'label': '', 'value': True}],
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

        ### H2 SPECTRA PLOT
        dcc.Graph(
            id='h2-spectra-plot-chan1',
            style={
                'position': 'absolute',
                'top': '275px',
                'right': '265px',
                'width': '250px',
                'height': '25%',
                'border': 'none',
                'backgroundColor': ''
            },
            config={'displayModeBar': False},
            figure={
                'data': [],
                'layout': {
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False},
                    'margin': {'l': 35, 'r': 10, 't': 35, 'b': 35}
                }
            }
        ),
        dcc.Graph(
            id='h2-spectra-plot-chan2',
            style={
                'position': 'absolute',
                'top': '275px',
                'right': '15px',
                'width': '250px',
                'height': '25%',
                'border': 'none',
                'backgroundColor': 'white'
            },
            config={'displayModeBar': False},
            figure={
                'data': [],
                'layout': {
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False},
                    'margin': {'l': 0, 'r': 10, 't': 35, 'b': 35}
                }
            }
        ),
        html.Div(
            id="h2-spectra-plot-text",
            style={
                'position': 'absolute',
                'top': '275px',
                'right': '15px',
                'width': '500px',
                'height': '25%',
                'border': '1px solid black',
                'backgroundColor': 'rgba(0,0,0,0)',
                'pointerEvents': 'none',
                'zIndex': 1000,
                'display': 'flex',
                'justifyContent': 'center',
            },
            children=html.Div(
                style={
                    'fontFamily': 'Arial',
                    'fontSize': '18px',
                    'color': '#414141',
                    'padding': '3px'
                },
                children="Click on a pixel to see its data"
            )
        ),

        ### IUE SPECTRA PLOT
        dcc.Graph(
            id='IUE-spectra-plot',
            style={
                'position': 'absolute',
                'bottom': '125px',
                'right': '15px',
                'width': '500px',
                'height': '25%', # 35%
                'border': '1px solid black',
                'backgroundColor': 'white'
            },
            config={'displayModeBar': False},
            figure={
                'data': [],
                'layout': {
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False},
                    'margin': {'l': 10, 'r': 10, 't': 35, 'b': 35},
                    'title': 'Click on a star to see its data'
                }
            }
        ),

        ### SMALL NIGHTTIME VISIBILITY FRACTION PLOT
        dcc.Graph(
            id='nighttime-frac-plot',
            style={
                'position': 'absolute',
                'bottom': '25px',
                'right': '100px',
                'width': '13%',
                'height': '10%',
                'border': 'none'
            },
            config={'staticPlot': True},
            figure={
                'data': [],
                'layout': {
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False},
                    'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0}
                }
            }
        ),
        html.Div(
            [
                html.Div("O", style={'position': 'absolute', 'bottom': '-160px', 'right': '282.5px'}),
                html.Div("N", style={'position': 'absolute', 'bottom': '-160px', 'right': '249.5px'}),
                html.Div("D", style={'position': 'absolute', 'bottom': '-160px', 'right': '216.5px'}),
                html.Div("J", style={'position': 'absolute', 'bottom': '-160px', 'right': '186.5px'}),
                html.Div("F", style={'position': 'absolute', 'bottom': '-160px', 'right': '153.5px'}),
                html.Div("M", style={'position': 'absolute', 'bottom': '-160px', 'right': '117.5px'}),
                html.Div("0%", style={'position': 'absolute', 'bottom': '-147px', 'right': '300px'}),
                html.Div("100%", style={'position': 'absolute', 'bottom': '-73px', 'right': '300px'}),
            ],
            style={'position': 'absolute', 'width': '100%', 'height': '20px'}
        ),

        ### STAR INFO TEXT
        html.Div(
            id='clicked-star',
            style={
                'position': 'absolute',
                'bottom': '15px',
                'right': '360px',
                'width': '9%',
                'height': '11%',
                'padding': '0px',
                'backgroundColor': 'white',
                'fontSize': '14px',
                'fontFamily': 'Arial',
                'lineHeight': '1.5',
                'border': 'none'
            },
            children="Click on a star to see its information"
        ),

        ### SELECTED STAR TEXTBOX AND DOWNLOAD BUTTON
        html.Div(
            id='selected-stars',
            style={
                'border': '1px solid black', 'padding': '0px', 'overflowY': 'scroll',
                'height': '165px', 'width': '885px', 'position': 'absolute', 'bottom': '15px',
                'right': '535px', 'backgroundColor': 'white'
            }
        ),
        html.Button(
            "Download CSV",
            id="download-btn",
            style={
                "position": "absolute",
                "bottom": "190px",
                "right": "1270px",
                "fontSize": "18px",
                "width": "150px",
                "height": "40px"
            }
        ),
        dcc.Download(id="download-csv"),
    ]
    if args.local:
        children.extend([
            html.Button(
                "Spectral Fitting View",
                id="switch-to-alt-btn",
                style={
                    # "display": "none"
                    "position": "absolute",
                    "top": "20px",
                    "right": "20px",
                    "width": "250px",
                    "height": "50px",
                    "fontSize": "18px",
                    "fontFamily": 'Arial',
                }
            ),
            html.Button(id="switch-to-main-btn", style={"display": "none"})
        ])
    else:
        children.extend([
            html.Button(id="switch-to-alt-btn", style={"display": "none"}),
            html.Button(id="switch-to-main-btn", style={"display": "none"})
        ])

    return html.Div(
        id="main-container",
        children=children
    )

def alt_layout():

    children=[
        
        ### HIDDEN COMPONENTS
        html.Button(id="scatter-plot", style={"display": "none"}),
        html.Div([dcc.Checklist(id='show-spectra-checkbox')]),
        html.Div([dcc.Checklist(id='show-bg-checkbox')]),
        html.Div([dcc.Checklist(id='norm-spectra-checkbox')]),
        html.Div([dcc.Checklist(id='show-cont-checkbox')]),
        html.Div([dcc.Graph(id='nighttime-frac-plot', style={"display": "none"})]),
        html.Div(id="clicked-star", style={"display": "none"}),
        html.Button(id="download-btn", style={"display": "none"}),
        html.Div([dcc.Download(id='download-csv')]),
        html.Div(id="selected-stars", style={"display": "none"}),

        html.Div([dcc.Graph(id='h2-spectra-plot-chan1', style={"display": "none"})]),
        html.Div([dcc.Graph(id='h2-spectra-plot-chan2', style={"display": "none"})]),
        html.Div(id="h2-spectra-plot-text", style={"display": "none"})
    ]
    if args.local:
        children.extend([
            html.Button(
                "Exploratory View",
                id="switch-to-main-btn",
                style={
                    "position": "absolute",
                    "top": "20px",
                    "right": "20px",
                    "width": "250px",
                    "height": "50px",
                    "fontSize": "18px",
                    "fontFamily": 'Arial',
                }
            ),
            html.Button(id="switch-to-alt-btn", style={"display": "none"})
        ])
    else:
        children.extend([
            html.Button(id="switch-to-main-btn", style={"display": "none"}),
            html.Button(id="switch-to-alt-btn", style={"display": "none"})
        ])


    return html.Div(
        id="alt-container",
        children=children
    )

def default_layout():
    return html.Div(
        id="default-container",
        children=[

            dcc.Store(id="show-spectra-checkbox-store", data=[]),
            dcc.Store(id="show-bg-checkbox-store", data=[]),
            dcc.Store(id="norm-spectra-checkbox-store", data=[]),
            dcc.Store(id="show-cont-checkbox-store", data=[]),
            dcc.Store(id="scatter-store", data=None),
            dcc.Store(id="clicked-star-store", data=None),
            dcc.Store(id="selected-stars-store", data=None),
            dcc.Store(id="clicked-bg-store", data=None),

            dcc.Store(id="layout-store", data="main"),
            html.Div(id="dynamic-layout",
                     children=main_layout())
        ]
    )