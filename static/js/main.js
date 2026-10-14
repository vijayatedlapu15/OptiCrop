// OptiCrop main javascript logic file
// Interactivity, slider sync, AJAX forms, and Chart.js dashboards

document.addEventListener("DOMContentLoaded", () => {
    // 1. Display Current Date
    const dateEl = document.getElementById("current-date");
    if (dateEl) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        dateEl.textContent = new Date().toLocaleDateString('en-US', options);
    }

    // Engine Health Check
    checkEngineHealth();

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

    // 6. Plant Disease Detection Handlers
    if (document.getElementById("disease-dropzone")) {
        setupDiseaseDetection();
    }

    // 7. Weather Autofill for Recommendation Form
    if (document.getElementById("btn-toggle-weather-box")) {
        setupWeatherAutofill();
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

let rawDashboardData = null;
let evaluationData = null;

/**
 * SCENARIO 3: Load dashboard visualizations, model evaluations, and policy recommendations
 */
function loadResearchDashboard() {
    // 1. Fetch genuine Random Forest test set evaluation metrics
    fetch("/api/model-evaluation")
        .then(res => res.json())
        .then(data => {
            if (data.metrics) {
                evaluationData = data;
                const accEl = document.getElementById("val-acc");
                if (accEl) accEl.textContent = data.metrics.accuracy + "%";
                const f1WEl = document.getElementById("val-f1-weighted");
                const f1W = data.metrics.f1_weighted ?? data.metrics.weighted_f1;
                if (f1WEl && f1W) f1WEl.textContent = f1W + "%";
                const precEl = document.getElementById("val-prec-macro");
                const precM = data.metrics.precision_macro ?? data.metrics.macro_precision;
                if (precEl && precM) precEl.textContent = precM + "%";
                const recEl = document.getElementById("val-rec-macro");
                const recM = data.metrics.recall_macro ?? data.metrics.macro_recall;
                if (recEl && recM) recEl.textContent = recM + "%";

                // Default active tab is Feature Importance
                renderFeatureImportanceChart(data);
            }
        })
        .catch(err => console.error("Error loading model evaluation:", err));

    // 2. Fetch dataset agro-ecological statistics
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

            // Populate Crop Comparison Selectors
            if (data.crops && data.crops.length > 0) {
                setupCropComparison(data.crops);
            }

            // Setup chart toggle buttons
            const buttons = document.querySelectorAll(".selector-btn");
            const explanationBox = document.getElementById("chart-explanation");

            buttons.forEach(btn => {
                btn.addEventListener("click", (e) => {
                    buttons.forEach(b => b.classList.remove("active"));
                    btn.classList.add("active");
                    
                    const chartType = btn.getAttribute("data-chart");
                    
                    const canvas = document.getElementById("researchLargeChart");
                    const heatmap = document.getElementById("heatmap-container");

                    if (chartType === "correlation") {
                        canvas.style.display = "none";
                        heatmap.style.display = "block";
                        renderCorrelationHeatmap(data);
                        if (explanationBox) {
                            explanationBox.innerHTML = '<p><i class="fa-solid fa-circle-info"></i> <strong>Pearson Correlation:</strong> Displays linear correlation coefficients across all 7 environmental parameters in the 2,200 sample benchmark dataset.</p>';
                        }
                    } else {
                        canvas.style.display = "block";
                        heatmap.style.display = "none";
                        
                        if (chartType === "importance") {
                            if (evaluationData) {
                                renderFeatureImportanceChart(evaluationData);
                            }
                            if (explanationBox) {
                                explanationBox.innerHTML = '<p><i class="fa-solid fa-circle-info"></i> <strong>Feature Importance:</strong> Measures Mean Decrease in Impurity (Gini importance) across 100 decision trees. Shows which variables the model relies on most during tree splits; does not imply direct physical causation.</p>';
                            }
                        } else if (chartType === "nutrients") {
                            renderMacronutrientsChart(data);
                            if (explanationBox) {
                                explanationBox.innerHTML = '<p><i class="fa-solid fa-circle-info"></i> <strong>Macronutrients:</strong> Compares empirical average Nitrogen (N), Phosphorus (P), and Potassium (K) requirements (kg/ha) across all 22 crop classes.</p>';
                            }
                        } else if (chartType === "climate") {
                            renderClimateChart(data);
                            if (explanationBox) {
                                explanationBox.innerHTML = '<p><i class="fa-solid fa-circle-info"></i> <strong>Climatic Dual Axis:</strong> Displays average annual rainfall (mm) alongside optimal temperature (°C) per crop.</p>';
                            }
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

/**
 * Live Machine Learning Engine Status Ping
 */
function checkEngineHealth() {
    const badge = document.getElementById("engine-status-badge");
    if (!badge) return;

    fetch("/api/health")
        .then(res => res.json())
        .then(data => {
            if (data.status === "online") {
                badge.className = "theme-badge engine-online";
                badge.innerHTML = '<span class="engine-indicator engine-indicator-online"></span> ML Engine: Active';
                badge.title = "Random Forest (22 crops) & MobileNetV2 (38 pathologies) loaded successfully.";
            } else {
                badge.className = "theme-badge engine-degraded";
                badge.innerHTML = '<span class="engine-indicator engine-indicator-offline"></span> ML Engine: Degraded';
            }
        })
        .catch(() => {
            badge.className = "theme-badge engine-offline";
            badge.innerHTML = '<span class="engine-indicator engine-indicator-offline"></span> ML Engine: Offline';
        });
}

/**
 * Renders Genuine Random Forest Feature Importance Chart (Gini Impurity)
 */
function renderFeatureImportanceChart(evalData) {
    if (researchMainChart) {
        researchMainChart.destroy();
    }
    
    const canvas = document.getElementById("researchLargeChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    let labels = [];
    let dataVals = [];

    if (Array.isArray(evalData.feature_importance)) {
        labels = evalData.feature_importance.map(item => item.name || item.feature);
        dataVals = evalData.feature_importance.map(item => item.importance_percentage);
    } else if (evalData.feature_importance && evalData.feature_importance.features) {
        const featObj = evalData.feature_importance;
        const friendlyLabels = {
            'rainfall': 'Rainfall (mm)',
            'humidity': 'Relative Humidity (%)',
            'K': 'Potassium / K (kg/ha)',
            'P': 'Phosphorus / P (kg/ha)',
            'N': 'Nitrogen / N (kg/ha)',
            'temperature': 'Temperature (°C)',
            'ph': 'Soil pH'
        };
        labels = featObj.features.map(f => friendlyLabels[f] || f);
        dataVals = featObj.importances.map(v => +(v * 100).toFixed(2));
    } else {
        labels = ['Rainfall (mm)', 'Relative Humidity (%)', 'Potassium / K (kg/ha)', 'Phosphorus / P (kg/ha)', 'Nitrogen / N (kg/ha)', 'Temperature (°C)', 'Soil pH'];
        dataVals = [22.70, 21.13, 18.12, 14.36, 10.89, 7.57, 5.23];
    }

    researchMainChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Gini Impurity Contribution (%)',
                data: dataVals,
                backgroundColor: [
                    'rgba(43, 203, 186, 0.85)',
                    'rgba(52, 152, 219, 0.85)',
                    'rgba(253, 150, 68, 0.85)',
                    'rgba(155, 89, 182, 0.85)',
                    'rgba(46, 204, 113, 0.85)',
                    'rgba(252, 92, 156, 0.85)',
                    'rgba(241, 196, 15, 0.85)'
                ],
                borderColor: [
                    '#2bcbba',
                    '#3498db',
                    '#fd9644',
                    '#9b59b6',
                    '#2ecc71',
                    '#fc5c9c',
                    '#f1c40f'
                ],
                borderWidth: 1.5,
                borderRadius: 5
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#a0a8a3', font: { family: 'Outfit', size: 11 } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${context.parsed.x}% of overall decision split impurity`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#a0a8a3', font: { family: 'Outfit', size: 10 } },
                    title: { display: true, text: 'Mean Decrease in Impurity / Gini Importance (%)', color: '#a0a8a3' },
                    max: 30
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#f5f6fa', font: { family: 'Outfit', size: 11, weight: '500' } }
                }
            }
        }
    });
}

/**
 * Crop Comparison Tool Handlers & Selectors
 */
let cropCompareRadarChart = null;

function setupCropComparison(cropsList) {
    const selA = document.getElementById("compare-crop-a");
    const selB = document.getElementById("compare-crop-b");
    const btnCompare = document.getElementById("btn-run-comparison");
    const container = document.getElementById("comparison-results-container");
    const disclaimer = document.getElementById("comparison-disclaimer");

    if (!selA || !selB || !btnCompare) return;

    selA.innerHTML = "";
    selB.innerHTML = "";

    const sortedCrops = [...cropsList].sort();
    sortedCrops.forEach((crop, idx) => {
        const optA = document.createElement("option");
        optA.value = crop.toLowerCase();
        optA.textContent = crop;
        if (crop.toLowerCase() === "rice") optA.selected = true;
        selA.appendChild(optA);

        const optB = document.createElement("option");
        optB.value = crop.toLowerCase();
        optB.textContent = crop;
        if (crop.toLowerCase() === "maize" || (idx === 1 && !selB.value)) optB.selected = true;
        selB.appendChild(optB);
    });

    btnCompare.addEventListener("click", () => {
        const crop1 = selA.value;
        const crop2 = selB.value;

        if (crop1 === crop2) {
            alert("Please select two distinct crops to evaluate their agronomic differences.");
            return;
        }

        const origHtml = btnCompare.innerHTML;
        btnCompare.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Comparing...';
        btnCompare.disabled = true;

        fetch(`/api/compare-crops?crop1=${encodeURIComponent(crop1)}&crop2=${encodeURIComponent(crop2)}`)
            .then(res => res.json())
            .then(data => {
                btnCompare.innerHTML = origHtml;
                btnCompare.disabled = false;

                if (data.error) {
                    alert("Error: " + data.error);
                    return;
                }

                container.style.display = "grid";
                if (disclaimer) disclaimer.style.display = "block";
                container.scrollIntoView({ behavior: 'smooth' });

                document.getElementById("th-crop-a").textContent = data.crop1;
                document.getElementById("th-crop-b").textContent = data.crop2;

                const tbody = document.getElementById("comparison-table-body");
                tbody.innerHTML = "";

                const params = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];
                params.forEach(paramKey => {
                    const item = data.parameters[paramKey];
                    if (!item) return;

                    const diffVal = item.difference;
                    const diffSign = diffVal > 0 ? `+${diffVal}` : `${diffVal}`;
                    const diffBadgeClass = Math.abs(item.percent_diff) > 25 ? 'diff-high' : 'diff-normal';

                    const row = `
                        <tr>
                            <td><strong>${item.param_name}</strong></td>
                            <td><span class="unit-pill">${item.unit}</span></td>
                            <td><span class="crop-val crop-a-val">${item.crop1.mean}</span> <small class="text-muted">(${item.crop1.optimal_range})</small></td>
                            <td><span class="crop-val crop-b-val">${item.crop2.mean}</span> <small class="text-muted">(${item.crop2.optimal_range})</small></td>
                            <td><span class="diff-tag ${diffBadgeClass}">${diffSign} ${item.unit} (${item.percent_diff > 0 ? '+' : ''}${item.percent_diff}%)</span></td>
                        </tr>
                    `;
                    tbody.insertAdjacentHTML("beforeend", row);
                });

                renderCropComparisonChart(data);
            })
            .catch(err => {
                btnCompare.innerHTML = origHtml;
                btnCompare.disabled = false;
                alert("Failed to fetch comparison: " + err.message);
            });
    });
}

function renderCropComparisonChart(data) {
    if (cropCompareRadarChart) {
        cropCompareRadarChart.destroy();
    }

    const canvas = document.getElementById("cropCompareChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const params = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];
    const paramLabels = ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall'];

    const benchmarks = {
        'N': 140,
        'P': 145,
        'K': 205,
        'temperature': 45,
        'humidity': 100,
        'ph': 10,
        'rainfall': 300
    };

    const c1Normalized = params.map(p => Math.min(100, Math.round((data.parameters[p].crop1.mean / benchmarks[p]) * 100)));
    const c2Normalized = params.map(p => Math.min(100, Math.round((data.parameters[p].crop2.mean / benchmarks[p]) * 100)));

    cropCompareRadarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: paramLabels,
            datasets: [
                {
                    label: data.crop1,
                    data: c1Normalized,
                    backgroundColor: 'rgba(46, 204, 113, 0.25)',
                    borderColor: '#2ecc71',
                    borderWidth: 2,
                    pointBackgroundColor: '#2ecc71',
                    pointRadius: 4
                },
                {
                    label: data.crop2,
                    data: c2Normalized,
                    backgroundColor: 'rgba(52, 152, 219, 0.25)',
                    borderColor: '#3498db',
                    borderWidth: 2,
                    pointBackgroundColor: '#3498db',
                    pointRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#f5f6fa', font: { family: 'Outfit', size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const pKey = params[ctx.dataIndex];
                            const raw = ctx.datasetIndex === 0 ? data.parameters[pKey].crop1.mean : data.parameters[pKey].crop2.mean;
                            const unit = data.parameters[pKey].unit;
                            return ` ${ctx.dataset.label}: ${raw} ${unit} (${ctx.parsed.r}% relative max envelope)`;
                        }
                    }
                }
            },
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
                    grid: { color: 'rgba(255, 255, 255, 0.08)' },
                    pointLabels: { color: '#a0a8a3', font: { family: 'Outfit', size: 10, weight: '500' } },
                    ticks: { display: false },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

/**
 * Scenario 4: Deep Learning Plant Disease Diagnosis
 */
function setupDiseaseDetection() {
    const dropzone = document.getElementById("disease-dropzone");
    const fileInput = document.getElementById("disease-file-input");
    const browseBtn = document.getElementById("browse-files-btn");
    const previewContainer = document.getElementById("disease-preview-container");
    const previewImg = document.getElementById("disease-preview-img");
    const fileNameEl = document.getElementById("preview-filename");
    const fileSizeEl = document.getElementById("preview-filesize");
    const removeBtn = document.getElementById("remove-image-btn");
    const analyzeBtn = document.getElementById("btn-analyze-disease");
    const resultsCard = document.getElementById("disease-results-card");

    let currentFile = null;

    if (browseBtn && fileInput) {
        browseBtn.addEventListener("click", () => fileInput.click());
    }

    if (dropzone) {
        dropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropzone.classList.add("dragover");
        });
        dropzone.addEventListener("dragleave", (e) => {
            e.preventDefault();
            dropzone.classList.remove("dragover");
        });
        dropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropzone.classList.remove("dragover");
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFileSelect(e.dataTransfer.files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }

    function handleFileSelect(file) {
        if (!file.type.match('image.*')) {
            alert("Please select a valid image file (JPG, PNG, WebP).");
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            alert("File size exceeds 10 MB limit.");
            return;
        }

        currentFile = file;
        if (fileNameEl) fileNameEl.textContent = file.name;
        if (fileSizeEl) fileSizeEl.textContent = (file.size / 1024).toFixed(1) + " KB";

        const reader = new FileReader();
        reader.onload = (e) => {
            if (previewImg) previewImg.src = e.target.result;
            if (previewContainer) previewContainer.style.display = "block";
            if (dropzone) dropzone.style.display = "none";
        };
        reader.readAsDataURL(file);
    }

    if (removeBtn) {
        removeBtn.addEventListener("click", () => {
            currentFile = null;
            if (fileInput) fileInput.value = "";
            if (previewImg) previewImg.src = "";
            if (previewContainer) previewContainer.style.display = "none";
            if (dropzone) dropzone.style.display = "block";
            if (resultsCard) resultsCard.style.display = "none";
        });
    }

    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", () => {
            if (!currentFile) {
                alert("Please select or drop an image of a crop leaf first.");
                return;
            }

            const origHtml = analyzeBtn.innerHTML;
            analyzeBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Running MobileNetV2 Inference...';
            analyzeBtn.disabled = true;

            const formData = new FormData();
            formData.append("image", currentFile);

            fetch("/api/disease-detection", {
                method: "POST",
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                analyzeBtn.innerHTML = origHtml;
                analyzeBtn.disabled = false;

                if (data.error) {
                    alert("Diagnosis Error: " + data.error);
                    return;
                }

                renderDiseaseResults(data);
            })
            .catch(err => {
                analyzeBtn.innerHTML = origHtml;
                analyzeBtn.disabled = false;
                alert("Network or inference error: " + err.message);
            });
        });
    }

    // Modal for 38 supported classes
    const openCatalogBtn = document.getElementById("btn-open-catalog");
    const catalogModal = document.getElementById("disease-catalog-modal");
    const closeCatalogBtn = document.getElementById("btn-close-catalog");

    if (openCatalogBtn && catalogModal) {
        openCatalogBtn.addEventListener("click", () => {
            catalogModal.style.display = "flex";
            loadDiseaseCatalog();
        });
    }

    if (closeCatalogBtn && catalogModal) {
        closeCatalogBtn.addEventListener("click", () => {
            catalogModal.style.display = "none";
        });
    }

    if (catalogModal) {
        catalogModal.addEventListener("click", (e) => {
            if (e.target === catalogModal) {
                catalogModal.style.display = "none";
            }
        });
    }
}

function renderDiseaseResults(data) {
    const card = document.getElementById("disease-results-card");
    if (!card) return;

    card.style.display = "block";
    card.scrollIntoView({ behavior: 'smooth' });

    const cropEl = document.getElementById("disease-result-crop");
    if (cropEl) cropEl.textContent = data.crop;
    const condEl = document.getElementById("disease-result-condition");
    if (condEl) condEl.textContent = data.condition;
    const confEl = document.getElementById("disease-result-confidence");
    if (confEl) confEl.textContent = data.confidence + "%";
    const fillEl = document.getElementById("disease-confidence-fill");
    if (fillEl) fillEl.style.width = data.confidence + "%";

    const badge = document.getElementById("disease-severity-badge");
    if (badge) {
        badge.textContent = data.severity.toUpperCase();
        badge.className = "severity-badge severity-" + data.severity.toLowerCase();
    }

    // Warning / Caution box for low-confidence
    const cautionBox = document.getElementById("disease-caution-box");
    if (cautionBox) {
        if (data.warning) {
            cautionBox.style.display = "block";
            const cautionText = document.getElementById("disease-caution-text");
            if (cautionText) cautionText.textContent = data.warning;
        } else {
            cautionBox.style.display = "none";
        }
    }

    // Symptoms
    const symEl = document.getElementById("disease-symptoms");
    if (symEl) symEl.textContent = data.symptoms;

    // Care recommendations
    const careList = document.getElementById("disease-care-list");
    if (careList) {
        careList.innerHTML = "";
        (data.care_recommendations || []).forEach(tip => {
            const li = document.createElement("li");
            li.innerHTML = '<i class="fa-solid fa-seedling text-emerald"></i> <span>' + tip + '</span>';
            careList.appendChild(li);
        });
    }

    // Prevention
    const prevEl = document.getElementById("disease-prevention");
    if (prevEl) {
        prevEl.textContent = data.prevention || "Maintain good soil aeration and cultural crop sanitation.";
    }

    // Top candidates
    const candContainer = document.getElementById("top-candidates-container");
    if (candContainer && data.top_candidates) {
        candContainer.innerHTML = "";
        data.top_candidates.forEach(cand => {
            candContainer.insertAdjacentHTML("beforeend", `
                <div class="candidate-row">
                    <div class="candidate-info">
                        <strong>${cand.crop}</strong> — ${cand.condition}
                    </div>
                    <div class="candidate-bar-wrapper">
                        <div class="candidate-bar-fill" style="width: ${cand.confidence}%"></div>
                        <span class="candidate-pct">${cand.confidence}%</span>
                    </div>
                </div>
            `);
        });
    }
}

function loadDiseaseCatalog() {
    const container = document.getElementById("catalog-grid");
    if (!container || container.children.length > 1) return;

    container.innerHTML = '<p class="text-muted"><i class="fa-solid fa-spinner fa-spin"></i> Loading 38-class pathology taxonomy...</p>';

    fetch("/api/disease-classes")
        .then(res => res.json())
        .then(data => {
            if (data.catalog) {
                container.innerHTML = "";
                Object.keys(data.catalog).sort().forEach(crop => {
                    const conditions = data.catalog[crop];
                    const cropCard = document.createElement("div");
                    cropCard.className = "catalog-crop-card";
                    cropCard.innerHTML = `
                        <h4><i class="fa-solid fa-leaf text-emerald"></i> ${crop} (${conditions.length})</h4>
                        <ul>
                            ${conditions.map(c => `<li><span class="${c.is_healthy ? 'text-healthy' : 'text-pathogen'}">${c.is_healthy ? '●' : '▲'}</span> ${c.condition}</li>`).join('')}
                        </ul>
                    `;
                    container.appendChild(cropCard);
                });
            }
        })
        .catch(err => {
            container.innerHTML = '<p class="text-danger">Failed to load pathology catalog.</p>';
        });
}

/**
 * Optional Live Weather Autofill via Open-Meteo API
 */
function setupWeatherAutofill() {
    const toggleBtn = document.getElementById("btn-toggle-weather-box");
    const weatherBox = document.getElementById("weather-fetcher-box");
    const cityInput = document.getElementById("weather-city-input");
    const fetchBtn = document.getElementById("btn-fetch-weather");
    const statusMsg = document.getElementById("weather-status-msg");

    if (toggleBtn && weatherBox) {
        toggleBtn.addEventListener("click", () => {
            const isHidden = weatherBox.style.display === "none";
            weatherBox.style.display = isHidden ? "block" : "none";
            if (isHidden && cityInput) cityInput.focus();
        });
    }

    if (fetchBtn && cityInput) {
        fetchBtn.addEventListener("click", () => {
            const city = cityInput.value.trim();
            if (!city) {
                showWeatherStatus("Please enter a city or district name.", "warning");
                return;
            }

            const origHtml = fetchBtn.innerHTML;
            fetchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Geocoding...';
            fetchBtn.disabled = true;

            showWeatherStatus(`Querying Open-Meteo for "${city}"...`, "info");

            // 1. Geocode
            fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`)
                .then(res => res.json())
                .then(geoData => {
                    if (!geoData.results || geoData.results.length === 0) {
                        throw new Error(`Location "${city}" not found. Try a major district or nearby capital.`);
                    }
                    const loc = geoData.results[0];
                    const locLabel = `${loc.name}, ${loc.country || ''}`;

                    fetchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Fetching climate...';

                    // 2. Fetch live weather
                    return fetch(`https://api.open-meteo.com/v1/forecast?latitude=${loc.latitude}&longitude=${loc.longitude}&current=temperature_2m,relative_humidity_2m&timezone=auto`)
                        .then(res => res.json())
                        .then(weatherData => {
                            if (!weatherData.current) {
                                throw new Error("Could not retrieve current weather conditions.");
                            }
                            const temp = Math.round(weatherData.current.temperature_2m * 10) / 10;
                            const hum = Math.round(weatherData.current.relative_humidity_2m);

                            // Autofill inputs
                            const tempInput = document.getElementById("input-temp");
                            const humInput = document.getElementById("input-hum");

                            if (tempInput) {
                                tempInput.value = temp;
                                tempInput.dispatchEvent(new Event('input'));
                            }
                            if (humInput) {
                                humInput.value = hum;
                                humInput.dispatchEvent(new Event('input'));
                            }

                            showWeatherStatus(`✓ Live climate loaded for ${locLabel}: Temperature ${temp}°C, Humidity ${hum}%. (Note: Soil N-P-K & annual rainfall must still be entered for your local agro-zone).`, "success");
                        });
                })
                .catch(err => {
                    showWeatherStatus(err.message, "error");
                })
                .finally(() => {
                    fetchBtn.innerHTML = origHtml;
                    fetchBtn.disabled = false;
                });
        });
    }

    function showWeatherStatus(text, type) {
        if (!statusMsg) return;
        statusMsg.style.display = "block";
        statusMsg.className = `weather-status-msg weather-status-${type}`;
        statusMsg.textContent = text;
    }
}

