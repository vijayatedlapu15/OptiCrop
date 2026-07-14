// OptiCrop main javascript logic file
// Interactivity, slider sync, AJAX forms, and Chart.js dashboards

document.addEventListener("DOMContentLoaded", () => {
    // 1. Display Current Date
    const dateEl = document.getElementById("current-date");
    if (dateEl) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        dateEl.textContent = new Date().toLocaleDateString('en-US', options);
    }

    // 2. Sync range sliders and number inputs
    setupSliderSync();

    // 3. Preset fillers for Recommendation Form
    setupPresets();

    // 4. Form AJAX Handlers
    setupFormHandlers();

    // 5. Scenario 3 Research Dashboards
    if (document.getElementById("researchLargeChart")) {
        loadResearchDashboard();
    }
});

/**
 * Syncs number inputs and range sliders when either changes
 */
function setupSliderSync() {
    const sliders = document.querySelectorAll(".sync-slider");
    sliders.forEach(slider => {
        const targetId = slider.getAttribute("data-target");
        const numberInput = document.getElementById(targetId);
        
        if (numberInput) {
            // Set slider initial value to match input
            if (numberInput.value) {
                slider.value = numberInput.value;
            }
            
            // Slider drag updates input
            slider.addEventListener("input", (e) => {
                numberInput.value = e.target.value;
                // Trigger change event on numberInput to update calculations if necessary
                numberInput.dispatchEvent(new Event('change'));
            });
            
            // Input changes update slider
            numberInput.addEventListener("input", (e) => {
                if (e.target.value) {
                    slider.value = e.target.value;
                }
            });
        }
    });
}

/**
 * Autofills forms with preset soil/climate data
 */
function setupPresets() {
    const presetBtns = document.querySelectorAll(".preset-btn");
    presetBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const data = btn.dataset;
            document.getElementById("input-n").value = data.n;
            document.getElementById("input-p").value = data.p;
            document.getElementById("input-k").value = data.k;
            document.getElementById("input-temp").value = data.temp;
            document.getElementById("input-hum").value = data.hum;
            document.getElementById("input-ph").value = data.ph;
            document.getElementById("input-rain").value = data.rain;
            
            // Sync all range sliders
            const sliders = document.querySelectorAll(".sync-slider");
            sliders.forEach(slider => {
                const targetId = slider.getAttribute("data-target");
                const numInput = document.getElementById(targetId);
                if (numInput) slider.value = numInput.value;
            });
        });
    });
}

// Global chart variables to allow updating/destroying
let recommendRadarChart = null;
let suitabilityRadarChart = null;
let researchMainChart = null;

/**
 * Handles Form submissions via AJAX
 */
function setupFormHandlers() {
    // SCENARIO 1: CROP RECOMMENDATION
    const recommendForm = document.getElementById("recommend-form");
    if (recommendForm) {
        recommendForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById("btn-submit-recommend");
            const originalHtml = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing Soil...';
            submitBtn.disabled = true;

            const formData = {
                N: parseFloat(document.getElementById("input-n").value),
                P: parseFloat(document.getElementById("input-p").value),
                K: parseFloat(document.getElementById("input-k").value),
                temperature: parseFloat(document.getElementById("input-temp").value),
                humidity: parseFloat(document.getElementById("input-hum").value),
                ph: parseFloat(document.getElementById("input-ph").value),
                rainfall: parseFloat(document.getElementById("input-rain").value)
            };

            fetch("/api/recommend", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            })
            .then(res => res.json())
            .then(data => {
                submitBtn.innerHTML = originalHtml;
                submitBtn.disabled = false;

                if (data.error) {
                    alert("Error: " + data.error);
                    return;
                }

                // Show result panel, hide empty state
                document.getElementById("recommend-empty-state").style.display = "none";
                const resultCard = document.getElementById("recommend-result-card");
                resultCard.style.display = "block";
                resultCard.scrollIntoView({ behavior: 'smooth' });

                // Fill details
                document.getElementById("crop-recommendation-name").textContent = data.crop;
                
                // Confidence bar
                document.getElementById("crop-confidence-val").textContent = data.confidence + "%";
                document.getElementById("crop-confidence-fill").style.width = data.confidence + "%";

                // Suitability bar
                document.getElementById("crop-suitability-val").textContent = data.suitability_score + "%";
                document.getElementById("crop-suitability-fill").style.width = data.suitability_score + "%";

                // Fill Table
                const tableBody = document.getElementById("details-table-body");
                tableBody.innerHTML = "";
                
                const features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];
                const displayNames = {
                    'N': 'Nitrogen (N)',
                    'P': 'Phosphorous (P)',
                    'K': 'Potassium (K)',
                    'temperature': 'Temperature (°C)',
                    'humidity': 'Humidity (%)',
                    'ph': 'Soil pH',
                    'rainfall': 'Rainfall (mm)'
                };

                features.forEach(feat => {
                    const item = data.details[feat];
                    const row = `
                        <tr>
                            <td><strong>${displayNames[feat]}</strong></td>
                            <td>${item.current}</td>
                            <td>${item.optimal_range}</td>
                            <td><span class="status-badge ${item.status_color}">${item.status}</span></td>
                        </tr>
                    `;
                    tableBody.insertAdjacentHTML('beforeend', row);
                });

                // Build Radar Chart
                buildRecommendRadar(data.crop, formData, data.details);
            })
            .catch(err => {
                console.error(err);
                submitBtn.innerHTML = originalHtml;
                submitBtn.disabled = false;
                alert("Server connection failed.");
            });
        });
    }

    // SCENARIO 2: CROP SUITABILITY ASSESSMENT
    const suitabilityForm = document.getElementById("suitability-form");
    if (suitabilityForm) {
        suitabilityForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById("btn-submit-suitability");
            const originalHtml = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Assessing Suitability...';
            submitBtn.disabled = true;

            const crop = document.getElementById("select-crop").value;
            const formData = {
                crop: crop,
                N: parseFloat(document.getElementById("input-n").value),
                P: parseFloat(document.getElementById("input-p").value),
                K: parseFloat(document.getElementById("input-k").value),
                temperature: parseFloat(document.getElementById("input-temp").value),
                humidity: parseFloat(document.getElementById("input-hum").value),
                ph: parseFloat(document.getElementById("input-ph").value),
                rainfall: parseFloat(document.getElementById("input-rain").value)
            };

            fetch("/api/suitability", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            })
            .then(res => res.json())
            .then(data => {
                submitBtn.innerHTML = originalHtml;
                submitBtn.disabled = false;

                if (data.error) {
                    alert("Error: " + data.error);
                    return;
                }

                // Show result panel, hide empty state
                document.getElementById("suitability-empty-state").style.display = "none";
                const resultCard = document.getElementById("suitability-result-card");
                resultCard.style.display = "block";
                resultCard.scrollIntoView({ behavior: 'smooth' });

                // Overall suitability percentage
                document.getElementById("suitability-overall-val").textContent = data.overall_score + "%";
                
                let desc = "Optimal Alignment";
                let strokeColor = "#2ecc71";
                if (data.overall_score < 40) {
                    desc = "Not Recommended";
                    strokeColor = "#e74c3c";
                } else if (data.overall_score < 75) {
                    desc = "Marginally Suitable";
                    strokeColor = "#f1c40f";
                }
                
                const descEl = document.getElementById("suitability-overall-desc");
                descEl.textContent = desc;
                descEl.className = "suitability-status-label";
                if (data.overall_score < 40) descEl.style.color = "var(--danger)";
                else if (data.overall_score < 75) descEl.style.color = "var(--accent)";
                else descEl.style.color = "var(--primary)";

                // Update Gauge path Dashoffset
                // Full dasharray for A 40 40 semicircle path is roughly 125.6
                // Dashoffset goes from 125.6 (0%) to 0 (100%)
                const dashoffset = 125.6 - (125.6 * (data.overall_score / 100));
                const gaugeFill = document.getElementById("gauge-fill");
                gaugeFill.setAttribute("stroke", strokeColor);
                gaugeFill.style.strokeDashoffset = dashoffset;

                // Build advice list
                const adviceList = document.getElementById("suitability-advice-list");
                adviceList.innerHTML = "";

                const features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];
                const displayNames = {
                    'N': 'Nitrogen (N) Content',
                    'P': 'Phosphorous (P) Content',
                    'K': 'Potassium (K) Content',
                    'temperature': 'Temperature Level',
                    'humidity': 'Humidity Level',
                    'ph': 'Soil pH Index',
                    'rainfall': 'Precipitation/Rainfall'
                };

                const iconMap = {
                    'N': 'fa-flask', 'P': 'fa-flask-vial', 'K': 'fa-mortar-pestle',
                    'temperature': 'fa-temperature-quarter', 'humidity': 'fa-droplet',
                    'ph': 'fa-eye-dropper', 'rainfall': 'fa-cloud-rain'
                };

                features.forEach(feat => {
                    const item = data.details[feat];
                    
                    let bgBadgeClass = item.status_color;
                    let iconName = iconMap[feat];
                    
                    let feedbackIcon = "fa-circle-check";
                    if (item.status_color === "warning") feedbackIcon = "fa-triangle-exclamation";
                    else if (item.status_color === "danger") feedbackIcon = "fa-circle-xmark";

                    const cardHtml = `
                        <div class="advice-card">
                            <div class="advice-icon-column text-${bgBadgeClass}">
                                <i class="fa-solid ${iconName}"></i>
                            </div>
                            <div class="advice-info-column">
                                <div class="advice-title">
                                    <span>${displayNames[feat]}</span> 
                                    <span class="status-badge ${bgBadgeClass}">${item.status} (${item.current})</span>
                                    <span class="label-info">Optimal: ${item.optimal_range}</span>
                                </div>
                                <div class="advice-text">
                                    <i class="fa-solid ${feedbackIcon} text-${bgBadgeClass}"></i> ${item.remediation}
                                </div>
                            </div>
                        </div>
                    `;
                    adviceList.insertAdjacentHTML('beforeend', cardHtml);
                });

                // Build Radar Chart
                buildSuitabilityRadar(crop, formData, data.details);
            })
            .catch(err => {
                console.error(err);
                submitBtn.innerHTML = originalHtml;
                submitBtn.disabled = false;
                alert("Server connection failed.");
            });
        });
    }
}

/**
 * Renders radar chart comparing current soil inputs with the recommended crop averages
 */
function buildRecommendRadar(cropName, inputs, details) {
    if (recommendRadarChart) {
        recommendRadarChart.destroy();
    }

    const ctx = document.getElementById("recommendRadarChart").getContext("2d");
    
    // Normalize properties on a relative scale (0 to 100) where 100 is the optimal mean
    const labels = ['Nitrogen', 'Phosphorus', 'Potassium', 'Temp', 'Humidity', 'pH', 'Rainfall'];
    const features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];
    
    const inputValues = [];
    const idealValues = [];
    
    features.forEach(feat => {
        const item = details[feat];
        // Relative values normalized by dividing by the mean (capped at 150%)
        const mean = item.mean || 1;
        inputValues.push(Math.min(150, (item.current / mean) * 100));
        idealValues.push(100); // The ideal mean is 100%
    });

    recommendRadarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Current Inputs (%)',
                    data: inputValues,
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    borderColor: '#3498db',
                    borderWidth: 2,
                    pointBackgroundColor: '#3498db'
                },
                {
                    label: 'Crop Optimal Mean (100%)',
                    data: idealValues,
                    backgroundColor: 'rgba(46, 204, 113, 0.08)',
                    borderColor: '#2ecc71',
                    borderWidth: 2,
                    pointBackgroundColor: '#2ecc71',
                    borderDash: [5, 5]
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#a0a8a3', font: { family: 'Outfit', size: 10 } }
                }
            },
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.06)' },
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    pointLabels: { color: '#a0a8a3', font: { family: 'Outfit', size: 9 } },
                    ticks: { display: false },
                    min: 0,
                    max: 150
                }
            }
        }
    });
}

/**
 * Renders radar chart comparing current inputs with target crop's ideal metrics
 */
function buildSuitabilityRadar(cropName, inputs, details) {
    if (suitabilityRadarChart) {
        suitabilityRadarChart.destroy();
    }

    const ctx = document.getElementById("suitabilityRadarChart").getContext("2d");
    const labels = ['Nitrogen', 'Phosphorus', 'Potassium', 'Temp', 'Humidity', 'pH', 'Rainfall'];
    const features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];
    
    const inputValues = [];
    const idealValues = [];
    
    features.forEach(feat => {
        const item = details[feat];
        const mean = item.mean || 1;
        inputValues.push(Math.min(150, (item.current / mean) * 100));
        idealValues.push(100);
    });

    suitabilityRadarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Soil Conditions (%)',
                    data: inputValues,
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    borderColor: '#3498db',
                    borderWidth: 2,
                    pointBackgroundColor: '#3498db'
                },
                {
                    label: `${cropName.toUpperCase()} Ideal (100%)`,
                    data: idealValues,
                    backgroundColor: 'rgba(46, 204, 113, 0.08)',
                    borderColor: '#2ecc71',
                    borderWidth: 2,
                    pointBackgroundColor: '#2ecc71',
                    borderDash: [5, 5]
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#a0a8a3', font: { family: 'Outfit', size: 10 } }
                }
            },
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.06)' },
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    pointLabels: { color: '#a0a8a3', font: { family: 'Outfit', size: 9 } },
                    ticks: { display: false },
                    min: 0,
                    max: 150
                }
            }
        }
    });
}

/**
 * SCENARIO 3: Load dashboard visualizations and policy recommendations
 */
function loadResearchDashboard() {
    let rawDashboardData = null;

    fetch("/api/research-data")
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                console.error("API error:", data.error);
                return;
            }
            rawDashboardData = data;
            
            // Build soil tags
            buildSoilPolicyTags(data.soil_groups);

            // Default display: Macronutrients
            renderMacronutrientsChart(data);

            // Setup chart toggle buttons
            const buttons = document.querySelectorAll(".selector-btn");
            buttons.forEach(btn => {
                btn.addEventListener("click", (e) => {
                    buttons.forEach(b => b.classList.remove("active"));
                    btn.classList.add("active");
                    
                    const chartType = btn.getAttribute("data-chart");
                    
                    // Hide heatmap container, show canvas
                    const canvas = document.getElementById("researchLargeChart");
                    const heatmap = document.getElementById("heatmap-container");

                    if (chartType === "correlation") {
                        canvas.style.display = "none";
                        heatmap.style.display = "block";
                        renderCorrelationHeatmap(data);
                    } else {
                        canvas.style.display = "block";
                        heatmap.style.display = "none";
                        
                        if (chartType === "nutrients") {
                            renderMacronutrientsChart(data);
                        } else if (chartType === "climate") {
                            renderClimateChart(data);
                        }
                    }
                });
            });

            // Setup policy tab buttons
            const tabBtns = document.querySelectorAll(".policy-tab-btn");
            tabBtns.forEach(btn => {
                btn.addEventListener("click", () => {
                    tabBtns.forEach(b => b.classList.remove("active"));
                    btn.classList.add("active");
                    
                    const targetTab = btn.getAttribute("data-tab");
                    const panes = document.querySelectorAll(".tab-pane");
                    panes.forEach(pane => {
                        pane.style.display = "none";
                    });
                    document.getElementById("pane-" + targetTab).style.display = "block";
                });
            });
        })
        .catch(err => console.error("Error fetching research data:", err));
}

function buildSoilPolicyTags(groups) {
    const listDrought = document.getElementById("tags-drought");
    const listWetland = document.getElementById("tags-wetland");
    const listAcidic = document.getElementById("tags-acidic");
    const listAlkaline = document.getElementById("tags-alkaline");
    
    // Drought
    listDrought.innerHTML = "";
    groups.drought_tolerant.forEach(crop => {
        listDrought.insertAdjacentHTML('beforeend', `<span class="crop-tag">${crop}</span>`);
    });
    
    // Wetland
    listWetland.innerHTML = "";
    groups.water_loving.forEach(crop => {
        listWetland.insertAdjacentHTML('beforeend', `<span class="crop-tag">${crop}</span>`);
    });
    
    // Acidic
    listAcidic.innerHTML = "";
    groups.acidic_tolerant.forEach(crop => {
        listAcidic.insertAdjacentHTML('beforeend', `<span class="crop-tag">${crop}</span>`);
    });
    
    // Alkaline
    listAlkaline.innerHTML = "";
    groups.alkaline_tolerant.forEach(crop => {
        listAlkaline.insertAdjacentHTML('beforeend', `<span class="crop-tag">${crop}</span>`);
    });
}

function renderMacronutrientsChart(data) {
    if (researchMainChart) {
        researchMainChart.destroy();
    }
    
    const ctx = document.getElementById("researchLargeChart").getContext("2d");
    researchMainChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.crops,
            datasets: [
                {
                    label: 'Avg Nitrogen (N)',
                    data: data.means.N,
                    backgroundColor: 'rgba(52, 152, 219, 0.75)',
                    borderColor: '#3498db',
                    borderWidth: 1
                },
                {
                    label: 'Avg Phosphorus (P)',
                    data: data.means.P,
                    backgroundColor: 'rgba(155, 89, 182, 0.75)',
                    borderColor: '#9b59b6',
                    borderWidth: 1
                },
                {
                    label: 'Avg Potassium (K)',
                    data: data.means.K,
                    backgroundColor: 'rgba(253, 150, 68, 0.75)',
                    borderColor: '#fd9644',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#a0a8a3', font: { family: 'Outfit', size: 11 } }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#a0a8a3', font: { family: 'Outfit', size: 9 }, maxRotation: 45, minRotation: 45 }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#a0a8a3', font: { family: 'Outfit', size: 10 } },
                    title: { display: true, text: 'Nutrient Content (mg/kg)', color: '#a0a8a3' }
                }
            }
        }
    });
}

function renderClimateChart(data) {
    if (researchMainChart) {
        researchMainChart.destroy();
    }
    
    const ctx = document.getElementById("researchLargeChart").getContext("2d");
    researchMainChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.crops,
            datasets: [
                {
                    label: 'Avg Rainfall (mm)',
                    data: data.means.rainfall,
                    borderColor: '#2bcbba',
                    backgroundColor: 'rgba(43, 203, 186, 0.08)',
                    borderWidth: 2,
                    fill: true,
                    yAxisID: 'yRain'
                },
                {
                    label: 'Avg Temp (°C)',
                    data: data.means.temperature,
                    borderColor: '#fc5c9c',
                    backgroundColor: 'rgba(252, 92, 156, 0)',
                    borderWidth: 2,
                    fill: false,
                    yAxisID: 'yTemp'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#a0a8a3', font: { family: 'Outfit', size: 11 } }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#a0a8a3', font: { family: 'Outfit', size: 9 }, maxRotation: 45, minRotation: 45 }
                },
                yRain: {
                    type: 'linear',
                    position: 'left',
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#2bcbba' },
                    title: { display: true, text: 'Rainfall (mm)', color: '#2bcbba' }
                },
                yTemp: {
                    type: 'linear',
                    position: 'right',
                    grid: { display: false },
                    ticks: { color: '#fc5c9c' },
                    title: { display: true, text: 'Temperature (°C)', color: '#fc5c9c' }
                }
            }
        }
    });
}

function renderCorrelationHeatmap(data) {
    const grid = document.getElementById("heatmap-grid");
    grid.innerHTML = "";
    
    const displayHeaders = ['', 'N', 'P', 'K', 'Temp', 'Hum', 'pH', 'Rain'];
    
    // Draw Header row
    displayHeaders.forEach(header => {
        grid.insertAdjacentHTML('beforeend', `<div class="heatmap-header-cell">${header}</div>`);
    });
    
    const features = ['N', 'P', 'K', 'Temp', 'Hum', 'pH', 'Rain'];
    
    for (let r = 0; r < 7; r++) {
        // Label cell
        grid.insertAdjacentHTML('beforeend', `<div class="heatmap-header-cell" style="text-align: right; padding-right: 8px;"><strong>${features[r]}</strong></div>`);
        
        for (let c = 0; c < 7; c++) {
            const coefficient = data.correlation[r][c];
            const displayVal = coefficient.toFixed(2);
            
            // Generate color: Positive red/orange, Negative blue, Neutral black
            let bgColor = "rgba(255, 255, 255, 0.02)";
            if (coefficient > 0.05) {
                // Positive correlation -> Green/Emerald strength
                bgColor = `rgba(46, 204, 113, ${coefficient * 0.9})`;
            } else if (coefficient < -0.05) {
                // Negative correlation -> Red/Crimson strength
                bgColor = `rgba(231, 76, 60, ${Math.abs(coefficient) * 0.9})`;
            }
            
            const cellHtml = `
                <div class="heatmap-cell" style="background-color: ${bgColor}" title="Correlation of ${features[r]} and ${features[c]} is ${displayVal}">
                    ${displayVal}
                </div>
            `;
            grid.insertAdjacentHTML('beforeend', cellHtml);
        }
    }
}
