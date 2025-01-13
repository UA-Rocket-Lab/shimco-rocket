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
    const plotResponse = await fetch('static/data/plot_data.json');
    plotData = await plotResponse.json();
}

// Initialize Plots Function
async function initializePlots() {
    await loadData();

    if (!plotData.length) {
        console.error("No data available to plot.");
        return;
    }

    // Get the checkbox element
    const checkbox = document.getElementById('show-spectra-checkbox');
    console.log("Checkbox element:", checkbox);

    if (!checkbox) {
        console.warn("Checkbox with id 'show-spectra' not found. No plot will be rendered.");
        return; // Exit the function without plotting
    }

    const filterHasSpectra = checkbox.checked; // true if checkbox is checked
    // console.log("Initial filter state:", filterHasSpectra);
    plotStars(filterHasSpectra);

    // Add Event Listener to Checkbox
    checkbox.addEventListener('change', function(e) {
        const isChecked = e.target.checked;
        // console.log("Checkbox state changed:", isChecked);
        plotStars(isChecked); // Replot based on checkbox state
    });
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
                GAL_LON: d["Galactic Longitude"].toFixed(2)
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
function plotStars(filterHasSpectra = false) {

    console.log("Checkbox state changed:", filterHasSpectra);

    const traces = generateTraces(filterHasSpectra);

    const layout = {
        hovermode: 'closest', // Ensures hover only activates on the closest point
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
                text: 'Spectral Type',
                font: {
                    size: 22,
                    color: '#333333'
                }
            },
            font: {
                size: 18,
                color: '#000000'
            },
            x: 1.1,
            y: 1.1,
            xanchor: "left",
            yanchor: "top"
        },
        shapes: generateGridLines() // Assuming you have this function defined
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

    // Render or Update Plotly Plot
    if (document.getElementById('scatter-plot').data) {
        // If plot already exists, update it
        Plotly.react('scatter-plot', traces, layout, config);
    } else {
        // Initial plot
        Plotly.newPlot('scatter-plot', traces, layout, config);
    }
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

// // Handle Checkbox Interactions
// function setupCheckboxListeners() {
//     // Show Spectra Checkbox
//     document.getElementById('show-spectra-checkbox').addEventListener('change', function() {
//         const showSpectra = this.checked;
//         // Assuming 'HasSpectra' is a field in plotData indicating availability
//         const filteredData = showSpectra ? plotData.filter(d => d["HasSpectra"]) : plotData;

//         // // Update Scatter Trace
//         // Plotly.restyle('scatter-plot', {
//         //     x: [filteredData.map(d => d["Galactic Longitude"])],
//         //     y: [filteredData.map(d => d["Galactic Latitude"])],
//         //     text: [filteredData.map(d => d["Name"])],
//         //     customdata: [filteredData.map(d => ({
//         //         Name: d["Name"],
//         //         SpectralType: d["Spectral Type"],
//         //         ApparentMagnitude: d["Apparent Magnitude"],
//         //         GAL_LAT: d["Galactic Latitude"],
//         //         GAL_LON: d["Galactic Longitude"]
//         //     }))],
//         //     'marker.size': [filteredData.map(d => d["Size"])],
//         //     'marker.color': [filteredData.map(d => d["Color"])]
//         // }, [1]); // Scatter trace index is 1

//         // Define color mapping for spectral types
//         const spectralColors = {
//             'O-type': '#1000FF',
//             'B-type': '#FF0000'
//         };

//         // Group plotData by Spectral Type
//         const groupedData = filteredData.reduce((acc, star) => {
//             const type = star["Color"];
//             if (!acc[type]) {
//                 acc[type] = [];
//             }
//             acc[type].push(star);
//             return acc;
//         }, {});

//         // Prepare Scatter Plot Traces
//         const scatterTraces = Object.keys(groupedData).map(type => {
//             const stars = groupedData[type];
//             return {
//                 x: stars.map(d => d["Galactic Longitude"]),
//                 y: stars.map(d => d["Galactic Latitude"]),
//                 customdata: stars.map(d => ({
//                     Name: d["Name"],
//                     SpectralType: d["Spectral Type"],
//                     ApparentMagnitude: d["Apparent Magnitude"].toFixed(2),
//                     GAL_LAT: d["Galactic Latitude"].toFixed(2),
//                     GAL_LON: d["Galactic Longitude"].toFixed(2)
//                 })),
//                 mode: 'markers',
//                 marker: {
//                     size: stars.map(d => d["Size"]),
//                     color: spectralColors[type], // Assign color based on spectral type
//                     line: { width: 0 }
//                 },
//                 name: `${type}`, // Legend entry
//                 type: 'scatter',
//                 hovertemplate:
//                     `<b>%{customdata.Name}</b><br>` +
//                     `Spectral Type: %{customdata.SpectralType}<br>` +
//                     `Apparent Magnitude: %{customdata.ApparentMagnitude}<br>` +
//                     `Galactic Latitude: %{customdata.GAL_LAT}°<br>` +
//                     `Galactic Longitude: %{customdata.GAL_LON}°<extra></extra>`
//             };
//     });

    // // Show Background Checkbox
    // document.getElementById('show-bg-checkbox').addEventListener('change', function() {
    //     const showBG = this.checked;
    //     Plotly.restyle('scatter-plot', { visible: showBG }, [0]); // Heatmap trace index is 0
    // });

    // // Normalize Spectra Checkbox
    // document.getElementById('norm-spectra-checkbox').addEventListener('change', function() {
    //     if(currentSelectedStar) {
    //         updateIUESpectraPlot(currentSelectedStar.Name);
    //     }
    // });

    // // Show Continuum Fit Checkbox
    // document.getElementById('show-cont-checkbox').addEventListener('change', function() {
    //     if(currentSelectedStar) {
    //         updateIUESpectraPlot(currentSelectedStar.Name);
    //     }
    // });
// }

function init() {
    initializePlots();
    // setupCheckboxListeners();
}

window.onload = init;