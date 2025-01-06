from dash import Dash, html, dcc

from data import main_fig

app = Dash(__name__)

# ==================================================
# Layout
# ==================================================

def main_layout():
    return html.Div(
        id="main-container",
        children=[

            ### STORE VARIABLES
            dcc.Store(id="show-spectra-checkbox-store", data=[]),
            dcc.Store(id="show-bg-checkbox-store", data=[]),
            dcc.Store(id="norm-spectra-checkbox-store", data=[]),
            dcc.Store(id="show-cont-checkbox-store", data=[]),
            dcc.Store(id="scatter-store", data=None),
            dcc.Store(id="clicked-star-store", data=None),

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
                        "Available Spectra:",
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
                        "Background:",
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
                        "Normalize Spectra:",
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
                        "Show Continuum Fit:",
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

            ### IUE SPECTRA PLOT
            dcc.Graph(
                id='IUE-spectra-plot',
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
                    html.Div("O", style={'position': 'absolute', 'bottom': '-155px', 'right': '267.5px'}),
                    html.Div("N", style={'position': 'absolute', 'bottom': '-155px', 'right': '234.5px'}),
                    html.Div("D", style={'position': 'absolute', 'bottom': '-155px', 'right': '201.5px'}),
                    html.Div("J", style={'position': 'absolute', 'bottom': '-155px', 'right': '168.5px'}),
                    html.Div("F", style={'position': 'absolute', 'bottom': '-155px', 'right': '135.5px'}),
                    html.Div("M", style={'position': 'absolute', 'bottom': '-155px', 'right': '102.5px'}),
                    html.Div("0%", style={'position': 'absolute', 'bottom': '-142px', 'right': '285px'}),
                    html.Div("100%", style={'position': 'absolute', 'bottom': '-68px', 'right': '285px'}),
                ],
                style={'position': 'relative', 'width': '100%', 'height': '20px'}
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
            dcc.Download(id="download-csv")
        ]
    )