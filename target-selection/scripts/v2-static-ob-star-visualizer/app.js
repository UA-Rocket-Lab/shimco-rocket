/* app.js */

// Global Variables
let plotData = [];
let integratedH2Map = [];

// Load Data
async function loadData() {
    const plotResponse = await fetch('static/data/plot_data.json');
    plotData = await plotResponse.json();

    const heatmapResponse = await fetch('static/data/integrated_h2_map.json');
    integratedH2Map = await heatmapResponse.json();
}

// Initialize Plots Function
async function initializePlots() {
    await loadData();

    if (!plotData.length) {
        console.error("No data available to plot.");
        return;
    }

    // Get the checkboxes
    const spectraCheckbox = document.getElementById('show-spectra-checkbox');
    const bgCheckbox = document.getElementById('show-bg-checkbox');

    // Initial states
    const filterHasSpectra = spectraCheckbox ? spectraCheckbox.checked : false;
    const showHeatmap = bgCheckbox ? bgCheckbox.checked : false;

    plotStars(filterHasSpectra, showHeatmap);

    // Add Event Listeners
    if (spectraCheckbox) {
        spectraCheckbox.addEventListener('change', function(e) {
            const isChecked = e.target.checked;
            plotStars(isChecked, bgCheckbox ? bgCheckbox.checked : false);
        });
    }

    if (bgCheckbox) {
        bgCheckbox.addEventListener('change', function(e) {
            const isChecked = e.target.checked;
            plotStars(spectraCheckbox ? spectraCheckbox.checked : false, isChecked);
        });
    }

    document.getElementById('IUE-spectra-plot').innerHTML = `
        <div class="iue-spectrum-message">
            Click on star to see its IUE spectrum
        </div>
    `;

    document.getElementById('star-info').innerHTML = `
        <div style="text-align: center;">
            Click on a star to see its information
        </div>
    `;

    // Add Plotly click event listener
    const plotElement = document.getElementById('scatter-plot');
    plotElement.on('plotly_click', handlePlotClick);
}

function generateTraces(filterHasSpectra) {
    const spectralColors = {
        'O-type': '#1000FF',
        'B-type': '#FF0000'
    };
    
    // Filter data based on "HasSpectra" if the filter is active
    const filteredData = filterHasSpectra
        ? plotData.filter(star => star["HasSpectra"] === true)
        : plotData;

    // Group data by Spectral Type
    const groupedData = filteredData.reduce((acc, star) => {
        const type = star["Color"];
        if (!acc[type]) {
            acc[type] = [];
        }
        acc[type].push(star);
        return acc;
    }, {});

    // Create Plotly traces for each Spectral Type
    const traces = Object.keys(groupedData).map(type => {
        const stars = groupedData[type];
        return {
            x: stars.map(d => d["Galactic Longitude"]),
            y: stars.map(d => d["Galactic Latitude"]),
            customdata: stars.map(d => ({
                Name: d["Name"],
                SpectralType: d["Spectral Type"],
                ApparentMagnitude: d["Apparent Magnitude"].toFixed(2),
                GAL_LAT: d["Galactic Latitude"].toFixed(2),
                GAL_LON: d["Galactic Longitude"].toFixed(2),
                HasSpectra: d["HasSpectra"],
                IUESpectra: d["IUESpectra"],
            })),
            mode: 'markers',
            marker: {
                size: stars.map(d => d["Size"]),
                color: spectralColors[type] || '#000000', // Default to black if type not found
                line: { width: 0 }
            },
            name: `${type} Stars`,
            type: 'scatter',
            hovertemplate:
                `<b>%{customdata.Name}</b><br>` +
                `Spectral Type: %{customdata.SpectralType}<br>` +
                `Apparent Magnitude: %{customdata.ApparentMagnitude}<br>` +
                `Galactic Latitude: %{customdata.GAL_LAT}°<br>` +
                `Galactic Longitude: %{customdata.GAL_LON}°<extra></extra>`
        };
    });

    return traces;
}

// Plotting Function
function plotStars(filterHasSpectra = false, showHeatmap = false) {
   
    const traces = generateTraces(filterHasSpectra);

    if (showHeatmap) {
        const heatmapTrace = generateHeatmapTrace();
        traces.unshift(heatmapTrace);

    }

    const layout = {
        hovermode: 'closest',
        xaxis: {
            title: 'Galactic Longitude (°)',
            range: [0, 360],
            ticklabelposition: "outside top",
            side: "top",
            showgrid: false
        },
        yaxis: {
            title: 'Galactic Latitude (°)',
            range: [-90, 90],
            showgrid: false
        },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        legend: {
            title: {
                text: 'Stars',
                font: {
                    size: 22,
                    color: '#333333'
                }
            },
            font: {
                size: 18,
                color: '#000000'
            },
            x: 1.07,
            y: 1.07,
            xanchor: "left",
            yanchor: "top"
        },
        shapes: generateGridLines()
    };

    const config = {
        responsive: true,
        modeBarButtonsToRemove: [
            'autoScale2d',
            'hoverClosestCartesian',
            'hoverCompareCartesian',
            'toggleSpikelines'
        ]
    };

    // Always use Plotly.react to update the plot
    Plotly.react('scatter-plot', traces, layout, config);
}

// Generate Grid Lines for Plot
function generateGridLines() {
    const shapes = [];

    // Latitude lines every 30 degrees
    for (let lat = -90; lat <= 90; lat += 30) {
        shapes.push({
            type: 'line',
            xref: 'x',
            yref: 'y',
            x0: 0,
            y0: lat,
            x1: 360,
            y1: lat,
            line: { color: 'gray', width: 0.5 }
        });
    }

    // Longitude lines every 30 degrees
    for (let lon = 0; lon <= 360; lon += 30) {
        shapes.push({
            type: 'line',
            xref: 'x',
            yref: 'y',
            x0: lon,
            y0: -90,
            x1: lon,
            y1: 90,
            line: { color: 'gray', width: 0.5 }
        });
    }

    return shapes;
}

function generateHeatmapTrace() {
    
    console.log(integratedH2Map)
    
    return {
        z: integratedH2Map.z,
        x: integratedH2Map.x,
        y: integratedH2Map.y,
        type: 'heatmap',
        colorscale: 'Viridis',
        showscale: false,
        zmin: 0,
        zmax: 5e5,
        hovertemplate:
        'Value: %{z}<br>' +
        'Galactic Latitude: %{y}°<br>' +
        'Galactic Longitude: %{x}°<extra></extra>'
    };
}

async function handlePlotClick(data) {
    if (data.points.length > 0) {
        const point = data.points[0];

        if (point.data.type === 'scatter') {
            const starData = point.customdata;

            if (starData) {
                // Update Clicked Star Info Box
                const infoHtml = `
                    <strong>Spectral Type:</strong> ${starData.SpectralType}<br>
                    <strong>Apparent Magnitude:</strong> ${starData.ApparentMagnitude}<br>
                    <strong>Galactic Latitude:</strong> ${starData.GAL_LAT}°<br>
                    <strong>Galactic Longitude:</strong> ${starData.GAL_LON}°
                `;
                document.getElementById('star-info').innerHTML = infoHtml;

                if (starData.HasSpectra) {
                    try {
                        const response = await fetch(starData.IUESpectra);
                        if (!response.ok) throw new Error('Spectrum data not found.');

                        const spectrumData = await response.json();

                        let traces = [];
                        if (spectrumData['wavelength'].length != 495) {
                            for (let i = 0; i < spectrumData['wavelength'].length; i++) {
                                const trace = {
                                    x: spectrumData['wavelength'][i],
                                    y: spectrumData['flux'][i],
                                    mode: 'lines',
                                    type: 'scatter',
                                    line: { color: 'black' }
                                };
                                traces.push(trace);
                            }
                        } else {
                            traces.push({
                                x: spectrumData['wavelength'],
                                y: spectrumData['flux'],
                                mode: 'lines',
                                type: 'scatter',
                                line: { color: 'black' }
                            });
                        }

                        Plotly.newPlot(
                            'IUE-spectra-plot',
                            traces,
                            {
                                xaxis: { title: 'Wavelength (Å)' },
                                yaxis: { title: 'Specific Flux Density' , showticklabels: false},
                                margin: {
                                    l: 40,
                                    r: 10,
                                    t: 10,
                                    b: 40
                                },
                                showlegend: false
                            },
                            { responsive: true }
                        );
                    } catch (error) {
                        console.error(error);
                        document.getElementById('IUE-spectra-plot').innerHTML = 'IUE Spectrum not available.';
                    }
                } else {
                    document.getElementById('IUE-spectra-plot').innerHTML = `
                        <div class="iue-spectrum-message">
                            No IUE spectrum available for this star
                        </div>
                    `;
                }
            }
        }
    }
}

function init() {
    initializePlots();
}

window.onload = init;