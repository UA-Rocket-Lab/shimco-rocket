from dash import Output, Input, State, ctx, html, no_update
from astropy.modeling import models, fitting
import plotly.graph_objs as go
import numpy as np
import io
import os

from layout import main_layout, alt_layout
from data import scatter_fig, SPECTRA_DIR, nighttime_frac

# ==================================================
# Callbacks
# ==================================================

def register_callbacks(app):

    ### LAYOUT RENDERING
    @app.callback(
        Output("layout-store", "data"),
        [Input("switch-to-alt-btn", "n_clicks"),
         Input("switch-to-main-btn", "n_clicks")]
    )
    def toggle_layout(switch_to_alt, switch_to_main):
        if ctx.triggered_id == "switch-to-alt-btn":
            return "alt"
        return "main"

    @app.callback(
        Output("dynamic-layout", "children"),
        Input("layout-store", "data"),
        prevent_initial_call=True
    )
    def render_layout(layout_store):
        if layout_store == "alt":
            return alt_layout()
        return main_layout()

    ### UPDATE PANELS
    @app.callback(
        [Output("download-csv", "data"),
         Output("selected-stars", "children")],
        [Input("download-btn", "n_clicks"),
         Input("scatter-plot", "selectedData")]
    )
    def selected_stars_textbox(_, selectedData):

        if selectedData is None or len(selectedData["points"]) == 0:
            return None, "Select stars using box select"
        else:
            star_data = [("MAIN_ID:", "SP_TYPE:", "m_V:", "GAL_LAT:", "GAL_LON:")] + \
            [ 
                (point["customdata"][0],
                 point["customdata"][1],
                 point["customdata"][2],
                 point["y"],
                 point["x"]) 
                for point in selectedData["points"]
            ]

            spacings = [35, 14, 12, 27, 0]
            html_vals = [
                html.Span("".join(str(row[j]).ljust(spacings[j]) for j in range(len(row))) + "\n")
                for row in star_data
            ]

            formatted_text = html.Div(
                html_vals,
                style={"whiteSpace": "pre-wrap", "fontFamily": "monospace"}
            )

            if ctx.triggered_id == "download-btn":
                buffer = io.StringIO()
                np.savetxt(buffer, np.array(star_data, dtype=str), delimiter=",", fmt="%s")
                content = buffer.getvalue()
                buffer.close()

                return {
                    "content": content,
                    "filename": "selected_stars.csv",
                    "type": "text/csv"
                }, formatted_text

            return None, formatted_text

    @app.callback(
        Output("IUE-spectra-plot", "figure"),
        [Input("scatter-plot", "clickData"),
         Input("norm-spectra-checkbox", "value"),
         Input("show-cont-checkbox", "value")]
    )
    def IUE_spectra_textbox(clickData, norm_spectra_checkbox, show_cont_checkbox):
        
        if clickData and 'customdata' in clickData['points'][0]:

            spectra_list = os.listdir(SPECTRA_DIR)
            star_name = clickData['points'][0]['customdata'][0].replace(' ', '_')
            if f"{star_name}.csv" in spectra_list:

                spectra = np.genfromtxt(f"{SPECTRA_DIR}{star_name}.csv", delimiter=',', dtype='float')
                if spectra.ndim == 1: spectra = spectra[np.newaxis, :]

                wavs = np.zeros((spectra.shape[0], int(spectra.shape[1]/2)))
                fluxs = np.zeros((spectra.shape[0], int(spectra.shape[1]/2)))
                for i, spec in enumerate(spectra):
                    wavs[i] = spec[:int(spectra.shape[1]/2)]
                    fluxs[i] = spec[int(spectra.shape[1]/2):]

                # Normalize spectra
                if norm_spectra_checkbox:
                    mean_val = np.mean(fluxs)
                    for i in range(fluxs.shape[0]):
                        fluxs[i] *= (mean_val / np.mean(fluxs[i,:]))
                
                # Calculate mean spectrum and fit continuum
                avg_wav = np.mean(wavs, axis=0)
                avg_flux = np.mean(fluxs, axis=0)

                mask = np.ones_like(avg_wav).astype('bool')
                regions = ['1150:1265','1375:1425','1515:1675']
                for region in regions:
                    lims = np.array(region.split(':')).astype('float')
                    mask *= np.invert((lims[0] < avg_wav) & (avg_wav < lims[1]))

                poly_init = models.Chebyshev1D(degree=3)
                fitter = fitting.LinearLSQFitter()
                cont_model = fitter(poly_init, avg_wav[mask], avg_flux[mask])
                cont_flux = cont_model(avg_wav)
                norm_flux = avg_flux / cont_flux

                # Plot shaded regions
                shaded_regions = [
                    go.Scatter(
                        x=[1395, 1405, 1405, 1395],
                        y=[np.min(fluxs), np.min(fluxs), np.max(fluxs), np.max(fluxs)],
                        fill='toself',
                        mode='none',
                        showlegend=False,
                        fillcolor='rgba(255, 200, 200, 0.5)'
                    ),
                    go.Scatter(
                        x=[1605, 1615, 1615, 1605],
                        y=[np.min(fluxs), np.min(fluxs), np.max(fluxs), np.max(fluxs)],
                        fill='toself',
                        mode='none',
                        showlegend=False,
                        fillcolor='rgba(200, 200, 255, 0.5)'
                    )
                ]

                # Plot individual spectra
                traces = [
                    go.Scatter(
                        x=wav,
                        y=flux,
                        mode='lines',
                        line_color='black',
                        line_width=2,
                        showlegend=False
                    ) for wav, flux in zip(wavs, fluxs)
                ]

                if show_cont_checkbox:
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

                return \
                {
                    'data': traces + shaded_regions,
                    'layout': {
                        'xaxis': {'title': 'Wavelength (Å)'},
                        'yaxis': {'showticklabels': False},
                        'margin': {'l': 10, 'r': 10, 't': 35, 'b': 35},
                        'title': f'Star: {star_name}'
                    }
                }
            else:
                return \
                {
                    'data': [],
                    'layout': {
                        'xaxis': {'visible': False},
                        'yaxis': {'visible': False},
                        'margin': {'l': 10, 'r': 10, 't': 35, 'b': 35},
                        'title': 'IUE spectrum unavailable for this star'
                    }
                }
        else:
            return \
            {
                'data': [],
                'layout': {
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False},
                    'margin': {'l': 10, 'r': 10, 't': 35, 'b': 35},
                    'title': 'Click on a star to see its spectrum'
                }
            }
    
    @app.callback(
        [Output("nighttime-frac-plot", "figure"),
         Output("clicked-star", "children")],
        Input("scatter-plot", "clickData")
    )
    def star_info(clickData):

        if clickData is None or 'customdata' not in clickData['points'][0]:
            return \
                {
                    'layout': {
                        'xaxis': {'range': [-0.5, 5.5], 'visible': False},
                        'yaxis': {'range': [-0.05, 1.05], 'visible': False},
                        'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0}
                    }
                }, \
                "Click on a star to see its information"
        else:

            x = [0, 1, 2, 3, 4, 5]
            y = nighttime_frac[np.where(nighttime_frac[:,0] == clickData['points'][0]['customdata'][0])[0][0],1:]

            star_data = [
                clickData['points'][0]['customdata'][1],
                clickData['points'][0]['customdata'][2],
                clickData['points'][0]['y'],
                clickData['points'][0]['x'],
            ]

            return \
                {
                    'data': [
                        {'x': x, 'y': y, 'mode': 'lines+markers', 'line': {'color': 'blue'}, 'marker': {'size': 8}}
                    ],
                    'layout': {
                        'xaxis': {'range': [-0.5, 5.5], 'visible': False},
                        'yaxis': {'range': [-5, 105], 'visible': False},
                        'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0}
                    }
                }, \
                html.Div([
                    html.P(f"SP_TYPE:   {star_data[0]}", style={"margin": "0"}),
                    html.P(f"m_V:       {star_data[1]:.2f}", style={"margin": "0"}),
                    html.P(f"GAL_LAT:   {star_data[2]:.4f}", style={"margin": "0"}),
                    html.P(f"GAL_LON:   {star_data[3]:.4f}", style={"margin": "0"})
                ])
    
    ### RESTORING STATES
    @app.callback(
        [Output("show-spectra-checkbox-store", "data"),
         Output("show-bg-checkbox-store", "data"),
         Output("norm-spectra-checkbox-store", "data"),
         Output("show-cont-checkbox-store", "data"),
         Output("show-spectra-checkbox", "value"),
         Output("show-bg-checkbox", "value"),
         Output("norm-spectra-checkbox", "value"),
         Output("show-cont-checkbox", "value"),
         Output("scatter-store", "data"),
         Output("scatter-plot", "figure")],
        [Input("switch-to-alt-btn", "n_clicks"),
         Input("switch-to-main-btn", "n_clicks"),
         Input("show-spectra-checkbox", "value"),
         Input("show-bg-checkbox", "value")],
        [State("norm-spectra-checkbox", "value"),
         State("show-cont-checkbox", "value"),
         State("show-spectra-checkbox-store", "data"),
         State("show-bg-checkbox-store", "data"),
         State("norm-spectra-checkbox-store", "data"),
         State("show-cont-checkbox-store", "data"),
         State("scatter-plot", "figure"),
         State("scatter-store", "data")],
        prevent_initial_call=True
    )
    def restore_checkboxes_and_scatter(to_alt_click,
                                       to_main_click,
                                       show_spectra_checkbox,
                                       show_bg_checkbox,
                                       norm_spectra_checkbox,
                                       show_cont_checkbox,
                                       show_spectra_store,
                                       show_bg_store,
                                       norm_spectra_store,
                                       show_cont_store,
                                       current_figure,
                                       stored_figure):

        # the order of these chunks doesn't seem logical but it is SUPER finicky. alter with caution

        # Store figure if limits are updated to something meaningful
        fig_to_store = no_update
        if current_figure is not None:
            if current_figure["layout"]["xaxis"]["range"] != [0,360]:
                fig_to_store = current_figure
                stored_figure = current_figure

        # Use current show_spectra and show_bg checkbox values if updated
        show_spectra = show_spectra_store
        show_bg = show_bg_store
        if show_spectra_checkbox or show_bg_checkbox:
            show_spectra = show_spectra_checkbox
            show_bg = show_bg_checkbox

        ##############

        # Store all values when switching to alt layout
        if ctx.triggered_id == 'switch-to-alt-btn' and to_alt_click:
            return show_spectra_checkbox, show_bg_checkbox, norm_spectra_checkbox, show_cont_checkbox, \
                no_update, no_update, no_update, no_update, \
                fig_to_store, no_update

        # Use stored figure limits if they exist
        fig_to_display = scatter_fig(show_spectra, show_bg)
        if stored_figure is not None:
            fig_to_display = scatter_fig(show_spectra, show_bg, stored_figure["layout"]["xaxis"]["range"], stored_figure["layout"]["yaxis"]["range"])

        # Handle all other cases
        return no_update, no_update, no_update, no_update, \
            show_spectra, show_bg, \
            norm_spectra_store, show_cont_store, \
            fig_to_store, fig_to_display