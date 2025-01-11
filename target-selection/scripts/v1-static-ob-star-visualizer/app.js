/* app.js */

// Global Variables
let plotData = [];
let integratedH2Map = [];
let nighttimeFrac = [];
let selectedStars = [];

// Current Selected Star
let currentSelectedStar = null;

// Load Data
async function loadData() {
    // Load plot_data.json
    const plotResponse = await fetch('static/data/plot_data.json');
    plotData = await plotResponse.json();

    // Load integrated_h2_map.json
    const h2MapResponse = await fetch('static/data/integrated_h2_map.json');
    integratedH2Map = await h2MapResponse.json();

    // Load nighttime_frac.json
    const nightFracResponse = await fetch('static/data/nighttime_frac.json');
    nighttimeFrac = await nightFracResponse.json();
}

// Initialize Plot
async function initializePlot() {
    // Load all necessary data
    await loadData();

    // Prepare Scatter Plot Trace
    const scatterTrace = {
        x: plotData.map(d => d["Galactic Longitude"]),
        y: plotData.map(d => d["Galactic Latitude"]),
        text: plotData.map(d => d["Name"]),
        customdata: plotData.map(d => ({
            Name: d["Name"],
            SpectralType: d["Spectral Type"],
            ApparentMagnitude: d["Apparent Magnitude"],
            GAL_LAT: d["Galactic Latitude"],
            GAL_LON: d["Galactic Longitude"]
        })),
        mode: 'markers',
        marker: {
            size: plotData.map(d => d["Size"]),
            color: plotData.map(d => d["Color"]),
            line: { width: 0 }
        },
        name: 'Stars',
        type: 'scatter'
    };

    // // Prepare Heatmap Trace (Background)
    // const heatmapTrace = {
    //     x: Array.from({length: 360}, (_, i) => i),
    //     y: Array.from({length: 180}, (_, i) => i - 90),
    //     z: integratedH2Map,
    //     type: 'heatmap',
    //     colorscale: 'Viridis',
    //     zmin: 0,
    //     zmax: 5e5,
    //     visible: false, // Initially hidden
    //     hovertemplate: 'GAL_LAT: %{y}<br>GAL_LON: %{x}<br>Value: %{z}<extra></extra>',
    //     name: 'H2 Integrated Emission'
    // };

    // Define Layout
    const layout = {
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
            title: { text: 'Spectral Type' },
            font: { size: 20 },
            x: 1.03,
            y: 1,
            xanchor: "left",
            yanchor: "top"
        },
        shapes: generateGridLines()
    };

    // Render Plot
    Plotly.newPlot('scatter-plot', [heatmapTrace, scatterTrace], layout);

    // Add Click Event Listener
    document.getElementById('scatter-plot').on('plotly_click', function(data){
        if(!data || !data.points || !data.points[0].customdata) return;

        const point = data.points[0].customdata;
        currentSelectedStar = point;

        // Display Star Information
        document.getElementById('clicked-star').innerHTML = `
            <p>SP_TYPE: ${point.SpectralType}</p>
            <p>m_V: ${point.ApparentMagnitude}</p>
            <p>GAL_LAT: ${point.GAL_LAT.toFixed(4)}°</p>
            <p>GAL_LON: ${point.GAL_LON.toFixed(4)}°</p>
        `;

        // Update H2 Spectra Plots
        updateH2SpectraPlots(point.GAL_LON, point.GAL_LAT);

        // Update IUE Spectra Plot
        updateIUESpectraPlot(point.Name);

        // Add to Selected Stars
        addToSelectedStars(point);
    });
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

// Handle Checkbox Interactions
function setupCheckboxListeners() {
    // Show Spectra Checkbox
    document.getElementById('show-spectra-checkbox').addEventListener('change', function() {
        const showSpectra = this.checked;
        // Assuming 'HasSpectra' is a field in plotData indicating availability
        const filteredData = showSpectra ? plotData.filter(d => d["HasSpectra"]) : plotData;

        // Update Scatter Trace
        Plotly.restyle('scatter-plot', {
            x: [filteredData.map(d => d["Galactic Longitude"])],
            y: [filteredData.map(d => d["Galactic Latitude"])],
            text: [filteredData.map(d => d["Name"])],
            customdata: [filteredData.map(d => ({
                Name: d["Name"],
                SpectralType: d["Spectral Type"],
                ApparentMagnitude: d["Apparent Magnitude"],
                GAL_LAT: d["Galactic Latitude"],
                GAL_LON: d["Galactic Longitude"]
            }))],
            'marker.size': [filteredData.map(d => d["Size"])],
            'marker.color': [filteredData.map(d => d["Color"])]
        }, [1]); // Scatter trace index is 1
    });

    // Show Background Checkbox
    document.getElementById('show-bg-checkbox').addEventListener('change', function() {
        const showBG = this.checked;
        Plotly.restyle('scatter-plot', { visible: showBG }, [0]); // Heatmap trace index is 0
    });

    // Normalize Spectra Checkbox
    document.getElementById('norm-spectra-checkbox').addEventListener('change', function() {
        if(currentSelectedStar) {
            updateIUESpectraPlot(currentSelectedStar.Name);
        }
    });

    // Show Continuum Fit Checkbox
    document.getElementById('show-cont-checkbox').addEventListener('change', function() {
        if(currentSelectedStar) {
            updateIUESpectraPlot(currentSelectedStar.Name);
        }
    });
}

// Update H2 Spectra Plots based on Clicked Star
function updateH2SpectraPlots(galLon, galLat) {
    // Find closest indices
    const latArray = Array.from({length: 180}, (_, i) => i - 90);
    const lonArray = Array.from({length: 360}, (_, i) => i);
    const latIdx = findClosestIndex(latArray, galLat);
    const lonIdx = findClosestIndex(lonArray, galLon);

    // Retrieve emission data for the selected pixel
    const emissionData = integratedH2Map[latIdx][lonIdx]; // Assuming this is an object with wavelengths and values for channels

    // For demonstration, let's assume emissionData has channels with wavelengths and values
    // Adjust according to your actual data structure

    // Example structure:
    // emissionData = {
    //     channels: {
    //         chan1: { wavelengths: [...], values: [...] },
    //         chan2: { wavelengths: [...], values: [...] }
    //     }
    // }

    // Since the actual data structure isn't provided, we'll mock the data
    const emissionDataMock = {
        channels: {
            chan1: {
                wavelengths: Array.from({length: 100}, (_, i) => 1395 + i * 0.2),
                values: Array.from({length: 100}, () => Math.random() * 1000)
            },
            chan2: {
                wavelengths: Array.from({length: 100}, (_, i) => 1605 + i * 0.2),
                values: Array.from({length: 100}, () => Math.random() * 1000)
            }
        }
    };

    // Prepare Channel 1 Plot
    const chan1Trace = {
        x: emissionDataMock.channels.chan1.wavelengths,
        y: emissionDataMock.channels.chan1.values,
        mode: 'lines',
        line: { color: 'black', width: 2 },
        showlegend: false
    };

    const shadedRegion1 = {
        x: [1395, 1405, 1405, 1395],
        y: [0, Math.max(...emissionDataMock.channels.chan1.values), Math.max(...emissionDataMock.channels.chan1.values), 0],
        fill: 'toself',
        fillcolor: 'rgba(255, 200, 200, 0.5)',
        line: { color: 'rgba(255,200,200,0)' },
        showlegend: false,
        mode: 'none'
    };

    // Render Channel 1 Plot
    Plotly.newPlot('h2-spectra-plot-chan1', [chan1Trace, shadedRegion1], {
        xaxis: { range: [1393, 1407], title: 'Wavelength (Å)' },
        yaxis: { showticklabels: false },
        margin: { l: 35, r: 10, t: 35, b: 35 }
    });

    // Prepare Channel 2 Plot
    const chan2Trace = {
        x: emissionDataMock.channels.chan2.wavelengths,
        y: emissionDataMock.channels.chan2.values,
        mode: 'lines',
        line: { color: 'black', width: 2 },
        showlegend: false
    };

    const shadedRegion2 = {
        x: [1605, 1615, 1615, 1605],
        y: [0, Math.max(...emissionDataMock.channels.chan2.values), Math.max(...emissionDataMock.channels.chan2.values), 0],
        fill: 'toself',
        fillcolor: 'rgba(200, 200, 255, 0.5)',
        line: { color: 'rgba(200,200,255,0)' },
        showlegend: false,
        mode: 'none'
    };

    // Render Channel 2 Plot
    Plotly.newPlot('h2-spectra-plot-chan2', [chan2Trace, shadedRegion2], {
        xaxis: { range: [1603, 1617], title: 'Wavelength (Å)' },
        yaxis: { showticklabels: false },
        margin: { l: 0, r: 10, t: 35, b: 35 }
    });

    // Update Text
    document.getElementById('h2-spectra-plot-text').innerHTML = `GAL_LAT: ${galLat.toFixed(2)}° / GAL_LON: ${galLon.toFixed(2)}°`;
}

// Find Closest Index in Array for a Given Value
function findClosestIndex(array, value) {
    return array.reduce((prev, curr, idx) => Math.abs(curr - value) < Math.abs(array[prev] - value) ? idx : prev, 0);
}

// Update IUE Spectra Plot based on Selected Star
function updateIUESpectraPlot(starName) {
    const formattedName = starName.replace(/ /g, '_');
    const spectraFile = `static/data/spectra/${formattedName}.json`;

    fetch(spectraFile)
        .then(response => {
            if(!response.ok) {
                throw new Error('Spectrum not available');
            }
            return response.json();
        })
        .then(data => {
            const { wavelengths, fluxes } = data;

            // Flatten wavelengths and fluxes if necessary
            const flatWavs = wavelengths.flat();
            const flatFlux = fluxes.flat();

            // Normalize Flux if Checkbox is Checked
            const normalize = document.getElementById('norm-spectra-checkbox').checked;
            let displayFlux = flatFlux.slice();
            if(normalize) {
                const meanVal = displayFlux.reduce((a, b) => a + b, 0) / displayFlux.length;
                displayFlux = displayFlux.map(f => f / meanVal);
            }

            // Create Trace for Spectrum
            const spectrumTrace = {
                x: flatWavs,
                y: displayFlux,
                mode: 'lines',
                line: { color: 'black', width: 2 },
                name: 'Spectrum'
            };

            // Continuum Fit
            const showCont = document.getElementById('show-cont-checkbox').checked;
            let traces = [spectrumTrace];

            if(showCont) {
                // Mock Continuum Data (Replace with actual continuum fit)
                const contWavs = flatWavs;
                const contFlux = displayFlux.map(f => f * 1.1); // Example modification

                const contTrace = {
                    x: contWavs,
                    y: contFlux,
                    mode: 'lines',
                    line: { color: 'blue', dash: 'dash', width: 2 },
                    name: 'Continuum Fit'
                };

                traces.push(contTrace);
            }

            // Shaded Regions
            const shadedRegions = [
                {
                    x: [1395, 1405, 1405, 1395],
                    y: [Math.min(...displayFlux), Math.min(...displayFlux), Math.max(...displayFlux), Math.max(...displayFlux)],
                    fill: 'toself',
                    fillcolor: 'rgba(255, 200, 200, 0.5)',
                    line: { color: 'rgba(255,200,200,0)' },
                    showlegend: false,
                    mode: 'none'
                },
                {
                    x: [1605, 1615, 1615, 1605],
                    y: [Math.min(...displayFlux), Math.min(...displayFlux), Math.max(...displayFlux), Math.max(...displayFlux)],
                    fill: 'toself',
                    fillcolor: 'rgba(200, 200, 255, 0.5)',
                    line: { color: 'rgba(200,200,255,0)' },
                    showlegend: false,
                    mode: 'none'
                }
            ];

            traces = traces.concat(shadedRegions);

            // Define Layout
            const layout = {
                title: `Star: ${starName}`,
                xaxis: { title: 'Wavelength (Å)' },
                yaxis: { showticklabels: false },
                margin: { l: 10, r: 10, t: 35, b: 35 }
            };

            // Render Plot
            Plotly.newPlot('IUE-spectra-plot', traces, layout);
        })
        .catch(error => {
            console.error('Error fetching spectra:', error);
            Plotly.newPlot('IUE-spectra-plot', [], {
                title: 'IUE spectrum unavailable for this star',
                xaxis: { visible: false },
                yaxis: { visible: false },
                margin: { l: 10, r: 10, t: 35, b: 35 }
            });
        });
}

// Add Selected Star to Selected Stars Textbox
function addToSelectedStars(point) {
    // Avoid duplicates
    if(selectedStars.find(s => s.Name === point.Name)) return;

    selectedStars.push(point);
    renderSelectedStars();
}

// Render Selected Stars in Textbox
function renderSelectedStars() {
    const container = document.getElementById('selected-stars');
    container.innerHTML = '';

    if(selectedStars.length === 0) {
        container.innerHTML = 'No stars selected.';
        return;
    }

    selectedStars.forEach(star => {
        const starDiv = document.createElement('div');
        starDiv.innerHTML = `
            <strong>${star.Name}</strong><br>
            SP_TYPE: ${star.SpectralType}<br>
            m_V: ${star.ApparentMagnitude}<br>
            GAL_LAT: ${star.GAL_LAT.toFixed(4)}°<br>
            GAL_LON: ${star.GAL_LON.toFixed(4)}°
        `;
        container.appendChild(starDiv);
    });
}

// Setup Download Button
function setupDownloadButton() {
    document.getElementById('download-btn').addEventListener('click', function() {
        if(selectedStars.length === 0) {
            alert('No stars selected for download.');
            return;
        }

        let csvContent = "MAIN_ID,SP_TYPE,m_V,GAL_LAT,GAL_LON\n";
        selectedStars.forEach(star => {
            csvContent += `${star.Name},${star.SpectralType},${star.ApparentMagnitude},${star.GAL_LAT.toFixed(4)},${star.GAL_LON.toFixed(4)}\n`;
        });

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.getElementById('download-link');
        link.setAttribute('href', url);
        link.setAttribute('download', 'selected_stars.csv');
        link.click();
    });
}

// Initialize Everything
function init() {
    initializePlot();
    // setupCheckboxListeners();
    // setupDownloadButton();
}

// Run Initialization on Page Load
window.onload = init;