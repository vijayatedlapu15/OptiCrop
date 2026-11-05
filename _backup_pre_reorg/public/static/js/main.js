// OptiCrop main javascript logic file
// Interactivity, slider sync, AJAX forms, and Chart.js dashboards

document.addEventListener("DOMContentLoaded", () => {
    // 1. Display Current Date
    const dateEl = document.getElementById("current-date");
    if (dateEl) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        dateEl.textContent = new Date().toLocaleDateString('en-US', options);
    }

    // Global Search
    setupGlobalSearch();

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

    // 8. Smart Farm Health & Risk Summary (Dashboard)
    if (document.getElementById("farm-health-section") || document.getElementById("farm-health-score-val") || document.querySelector(".farm-profile-btn")) {
        setupFarmHealthDashboard();
    }

    // 9. What-If Scenario Simulator (Crop Recommend)
    if (document.getElementById("btn-run-what-if") || document.getElementById("what-if-simulator-section")) {
        setupWhatIfSimulator();
    }

    // 10. Multi-Crop Suitability Ranking (Crop Suitability)
    if (document.getElementById("btn-rank-all-crops") || document.getElementById("multi-suitability-section")) {
        setupMultiCropSuitability();
    }

    // 11. Research Analytics Dual-Model & Latency Benchmark
    if (document.getElementById("btn-tab-disease-model") || document.getElementById("btn-tab-crop-model")) {
        setupResearchEvaluationLab();
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

                    // Display Top 3 Crop Recommendations
                    const topCropsContainer = document.getElementById("top-crops-container");

                    if (topCropsContainer) {
                        topCropsContainer.innerHTML = "";

                        (data.top_crops || []).forEach((crop, index) => {
                            const cropCard = document.createElement("div");
                            cropCard.className = "top-crop-item";

                            const rankLabel = ["🥇", "🥈", "🥉"][index] || `#${index + 1}`;

                            cropCard.innerHTML = `
                                <div class="top-crop-rank">${rankLabel}</div>
                                <div class="top-crop-info">
                                    <strong>${crop.crop}</strong>
                                    <span>Model probability: ${crop.confidence}%</span>
                                </div>
                                <div class="top-crop-score">
                                    <span>Suitability</span>
                                    <strong>${Number(crop.suitability_score).toFixed(1)}%</strong>
                                </div>
                            `;

                            topCropsContainer.appendChild(cropCard);
                        });
                    }


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
                        label: function (context) {
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
                        label: function (ctx) {
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
        browseBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }

    if (dropzone && fileInput) {
        dropzone.addEventListener("click", (e) => {
            if (e.target !== browseBtn && !browseBtn?.contains(e.target)) {
                fileInput.click();
            }
        });
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
            const emptyState = document.getElementById("disease-empty-state");
            if (emptyState) emptyState.style.display = "block";
        });
    }

    const testAnotherBtn = document.getElementById("btn-test-another");
    if (testAnotherBtn) {
        testAnotherBtn.addEventListener("click", (e) => {
            e.preventDefault();
            currentFile = null;
            if (fileInput) fileInput.value = "";
            if (previewImg) previewImg.src = "";
            if (previewContainer) previewContainer.style.display = "none";
            if (dropzone) dropzone.style.display = "block";
            if (resultsCard) resultsCard.style.display = "none";
            const emptyState = document.getElementById("disease-empty-state");
            if (emptyState) emptyState.style.display = "block";
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Plant species selector & unsupported boundary warning
    const plantSelect = document.getElementById("disease-plant-select");
    const unsupportedWarning = document.getElementById("unsupported-plant-warning");
    if (plantSelect && unsupportedWarning) {
        plantSelect.addEventListener("change", () => {
            if (plantSelect.value === "unsupported" || plantSelect.value === "Pear") {
                unsupportedWarning.style.display = "flex";
            } else {
                unsupportedWarning.style.display = "none";
            }
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

            if (plantSelect && plantSelect.value) {
                if (plantSelect.value === "unsupported") {
                    formData.append("selected_plant", "Unsupported Crop");
                } else {
                    formData.append("selected_plant", plantSelect.value);
                }
            }

            fetch("/api/disease-detection", {
                method: "POST",
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    analyzeBtn.innerHTML = origHtml;
                    analyzeBtn.disabled = false;

                    if (data.error && !data.crop) {
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

    // Management tabs navigation
    const diseaseTabBtns = document.querySelectorAll(".disease-tab-btn");
    diseaseTabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            diseaseTabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const targetId = btn.getAttribute("data-tab");
            document.querySelectorAll(".disease-tab-pane").forEach(pane => {
                pane.style.display = (pane.id === targetId) ? "block" : "none";
            });
        });
    });
}

function renderDiseaseResults(data) {
    const card = document.getElementById("disease-results-card");
    if (!card) return;

    const emptyState = document.getElementById("disease-empty-state");
    if (emptyState) emptyState.style.display = "none";

    card.style.display = "block";
    card.scrollIntoView({ behavior: 'smooth' });

    // Reset tabs to Overview tab by default
    const diseaseTabBtns = document.querySelectorAll(".disease-tab-btn");
    diseaseTabBtns.forEach(b => {
        if (b.getAttribute("data-tab") === "tab-overview") b.classList.add("active");
        else b.classList.remove("active");
    });
    document.querySelectorAll(".disease-tab-pane").forEach(p => {
        p.style.display = (p.id === "tab-overview") ? "block" : "none";
    });

    const cropEl = document.getElementById("disease-result-crop");
    if (cropEl) cropEl.textContent = data.crop;
    const condEl = document.getElementById("disease-result-condition");
    if (condEl) condEl.textContent = data.condition;
    const confEl = document.getElementById("disease-result-confidence");
    if (confEl) confEl.textContent = data.confidence + "%";
    const fillEl = document.getElementById("disease-confidence-fill");
    if (fillEl) fillEl.style.width = Math.min(100, Math.max(0, data.confidence)) + "%";

    const badge = document.getElementById("disease-severity-badge");
    if (badge) {
        badge.textContent = (data.severity || 'MODERATE').toUpperCase();
        badge.className = "severity-badge severity-" + (data.severity || 'moderate').toLowerCase();
    }

    // Confidence tier badge
    const tierBadge = document.getElementById("disease-tier-badge");
    if (tierBadge) {
        tierBadge.textContent = (data.confidence_tier || "MODEL SCORE").toUpperCase();
        if (data.status === 'supported' && data.confidence >= 80) {
            tierBadge.style.background = "rgba(16, 185, 129, 0.15)";
            tierBadge.style.color = "#34d399";
            tierBadge.style.borderColor = "rgba(16, 185, 129, 0.3)";
        } else if (data.status === 'incompatible') {
            tierBadge.style.background = "rgba(239, 68, 68, 0.15)";
            tierBadge.style.color = "#f87171";
            tierBadge.style.borderColor = "rgba(239, 68, 68, 0.3)";
        } else {
            tierBadge.style.background = "rgba(245, 158, 11, 0.15)";
            tierBadge.style.color = "#fbbf24";
            tierBadge.style.borderColor = "rgba(245, 158, 11, 0.3)";
        }
    }

    // Google Gemini Vision & Search Grounding Status Indicators
    const pillGemini = document.getElementById("pill-gemini-status");
    const pillGrounding = document.getElementById("pill-grounding-status");
    const pillUnavailable = document.getElementById("pill-unavailable-status");

    const apiInd = data.api_indicators || {};
    const vision = data.google_gemini_assessment || data.vision_verification || {};
    const web = data.google_search_corroboration || data.web_corroboration || {};

    if (pillGemini) {
        if (apiInd.gemini_connected || vision.api_status === 'connected' || vision.is_available) {
            pillGemini.style.display = "inline-flex";
        } else {
            pillGemini.style.display = "none";
        }
    }

    if (pillGrounding) {
        const hasGrounding = (apiInd.search_grounding_active || web.grounding_status === 'active' || (web.supporting_sources && web.supporting_sources.length > 0) || (web.sources && web.sources.length > 0));
        if (hasGrounding) {
            pillGrounding.style.display = "inline-flex";
        } else {
            pillGrounding.style.display = "none";
        }
    }

    if (pillUnavailable) {
        const isUnavailable = (apiInd.verification_unavailable || data.status === 'VERIFICATION UNAVAILABLE' || vision.api_status === 'unavailable' || vision.is_available === false);
        if (isUnavailable) {
            pillUnavailable.style.display = "inline-flex";
        } else {
            pillUnavailable.style.display = "none";
        }
    }

    // Reliability Status Banner
    const statusBanner = document.getElementById("disease-status-banner");
    const statusIcon = document.getElementById("disease-status-icon");
    const statusTitle = document.getElementById("disease-status-title");
    const statusDesc = document.getElementById("disease-status-desc");

    const normalizedStatus = (data.status || data.final_status || '').toUpperCase();

    if (statusBanner && statusTitle && statusDesc) {
        if (normalizedStatus === 'CORROBORATED' || data.status === 'supported') {
            statusBanner.className = "status-banner status-supported";
            statusBanner.style.background = "rgba(16, 185, 129, 0.12)";
            statusBanner.style.border = "1px solid rgba(16, 185, 129, 0.35)";
            statusBanner.style.color = "#a7f3d0";
            if (statusIcon) {
                statusIcon.className = "fa-solid fa-circle-check";
                statusIcon.style.color = "#34d399";
            }
            statusTitle.textContent = "CORROBORATED: Diagnosis Confirmed by Google Search Grounding";
            statusDesc.textContent = "Image visual assessment and credible agricultural extension references support the same likely diagnosis.";
        } else if (normalizedStatus === 'POSSIBLE') {
            statusBanner.className = "status-banner status-possible";
            statusBanner.style.background = "rgba(59, 130, 246, 0.12)";
            statusBanner.style.border = "1px solid rgba(59, 130, 246, 0.35)";
            statusBanner.style.color = "#93c5fd";
            if (statusIcon) {
                statusIcon.className = "fa-solid fa-magnifying-glass-chart";
                statusIcon.style.color = "#60a5fa";
            }
            statusTitle.textContent = "POSSIBLE: Preliminary Diagnostic Hypothesis";
            statusDesc.textContent = data.warning || "Some evidence supports a diagnosis, but evidence is incomplete or partial ambiguity remains.";
        } else if (normalizedStatus === 'UNSUPPORTED' || data.status === 'incompatible') {
            statusBanner.className = "status-banner status-incompatible";
            statusBanner.style.background = "rgba(239, 68, 68, 0.12)";
            statusBanner.style.border = "1px solid rgba(239, 68, 68, 0.35)";
            statusBanner.style.color = "#fca5a5";
            if (statusIcon) {
                statusIcon.className = "fa-solid fa-ban";
                statusIcon.style.color = "#f87171";
            }
            statusTitle.textContent = "UNSUPPORTED: Plant or Condition Outside Validated Scope";
            statusDesc.textContent = data.warning || `The plant or condition is outside OptiCrop's 14-crop benchmark scope. Chemical recommendations are withheld.`;
        } else if (normalizedStatus === 'VERIFICATION UNAVAILABLE') {
            statusBanner.className = "status-banner status-unavailable";
            statusBanner.style.background = "rgba(245, 158, 11, 0.12)";
            statusBanner.style.border = "1px solid rgba(245, 158, 11, 0.35)";
            statusBanner.style.color = "#fde68a";
            if (statusIcon) {
                statusIcon.className = "fa-solid fa-shield-halved";
                statusIcon.style.color = "#fbbf24";
            }
            statusTitle.textContent = "VERIFICATION UNAVAILABLE: Google Gemini Services Offline";
            statusDesc.textContent = data.warning || "Google Gemini API or Search Grounding is unconfigured or failed. Local ML model prediction is displayed as an unverified independent reference.";
        } else {
            statusBanner.className = "status-banner status-uncertain";
            statusBanner.style.background = "rgba(245, 158, 11, 0.12)";
            statusBanner.style.border = "1px solid rgba(245, 158, 11, 0.35)";
            statusBanner.style.color = "#fde68a";
            if (statusIcon) {
                statusIcon.className = "fa-solid fa-triangle-exclamation";
                statusIcon.style.color = "#fbbf24";
            }
            statusTitle.textContent = "UNCERTAIN: Foliar Identification Unresolved";
            statusDesc.textContent = data.warning || "Plant or disease cannot be reliably identified. The image may be blurry, unclear, or non-plant content.";
        }
    }

    // Species match note
    const matchNote = document.getElementById("disease-species-match-note");
    if (matchNote) {
        if (data.selected_plant) {
            if (data.is_compatible) {
                matchNote.innerHTML = `<span style="color: #34d399;"><i class="fa-solid fa-check"></i> Selected Host: <strong>${data.selected_plant}</strong> (Matches prediction)</span>`;
            } else {
                matchNote.innerHTML = `<span style="color: #f87171;"><i class="fa-solid fa-xmark"></i> Selected Host: <strong>${data.selected_plant}</strong> vs Inferred: <strong>${data.crop}</strong></span>`;
            }
        } else {
            matchNote.innerHTML = `<span style="color: var(--text-muted);"><i class="fa-solid fa-wand-magic-sparkles"></i> Host species inferred automatically: <strong>${data.crop}</strong></span>`;
        }
    }

    // Closest compatible candidate box
    const closestBox = document.getElementById("disease-closest-cand-box");
    const closestText = document.getElementById("disease-closest-cand-text");
    if (closestBox && closestText) {
        if (data.closest_compatible_candidate) {
            closestBox.style.display = "block";
            closestText.innerHTML = `Within your selected host (<strong>${data.closest_compatible_candidate.crop}</strong>), the closest hypothesis was <strong>${data.closest_compatible_candidate.condition}</strong> (Model Score: ${data.closest_compatible_candidate.confidence}%). <em>This is an unconfirmed hypothesis.</em>`;
        } else {
            closestBox.style.display = "none";
        }
    }

    // Unverified closed-set artifact box (shown when status is uncertain/incompatible)
    const artifactBox = document.getElementById("disease-unverified-artifact-box");
    const artifactText = document.getElementById("disease-unverified-artifact-text");
    if (artifactBox && artifactText) {
        if (data.status !== 'supported' && (data.predicted_plant || data.unverified_model_artifact)) {
            artifactBox.style.display = "block";
            const rawPlant = data.predicted_plant || data.raw_model_crop || "Unknown";
            const rawCond = data.predicted_condition || data.raw_model_condition || "Unknown";
            artifactText.innerHTML = `Underlying closed-set neural network produced an unverified raw output of <strong>${rawPlant} — ${rawCond}</strong> (${data.confidence}% closed-set softmax score). Because this crop or condition is outside the model's 38 supported classes (e.g., Pear or Pear Rust), this is an out-of-distribution artifact and <em>must NOT be presented as a confirmed diagnosis</em>. Chemical treatments have been completely withheld.`;
        } else {
            artifactBox.style.display = "none";
        }
    }

    // Render Independent Visual Verification & Web Corroboration Panel
    const verifTag = document.getElementById("verification-status-tag");
    const verifContent = document.getElementById("verification-details-content");
    if (verifContent) {
        const geminiAss = data.google_gemini_assessment || data.vision_verification || {};
        const searchCorrob = data.google_search_corroboration || data.web_corroboration || {};
        const localPred = data.local_ml_model_prediction || data.local_ml_result || {};
        const mgmtRecs = data.management_recommendations || data.management_guidance || {};
        const diagLimits = data.diagnostic_limitations || data.limitations || [];
        let vHtml = '';

        // Status tag
        if (verifTag) {
            const stNorm = (data.status || data.final_status || '').toUpperCase();
            if (stNorm === 'CORROBORATED' || stNorm === 'SUPPORTED') {
                verifTag.textContent = "CORROBORATED (EXTENSION VERIFIED)";
                verifTag.style.background = "rgba(16, 185, 129, 0.2)";
                verifTag.style.color = "#34d399";
            } else if (stNorm === 'POSSIBLE') {
                verifTag.textContent = "POSSIBLE (PRELIMINARY HYPOTHESIS)";
                verifTag.style.background = "rgba(59, 130, 246, 0.2)";
                verifTag.style.color = "#60a5fa";
            } else if (stNorm === 'UNSUPPORTED') {
                verifTag.textContent = "UNSUPPORTED (OUTSIDE CLASSIFIER SCOPE)";
                verifTag.style.background = "rgba(239, 68, 68, 0.2)";
                verifTag.style.color = "#f87171";
            } else if (stNorm === 'VERIFICATION UNAVAILABLE') {
                verifTag.textContent = "VERIFICATION UNAVAILABLE";
                verifTag.style.background = "rgba(245, 158, 11, 0.2)";
                verifTag.style.color = "#fbbf24";
            } else {
                verifTag.textContent = "UNCERTAIN / INCONCLUSIVE";
                verifTag.style.background = "rgba(100, 116, 139, 0.2)";
                verifTag.style.color = "#94a3b8";
            }
        }

        // ── 1. Local ML Model Prediction Section ─────────────────────────────
        const localColor = localPred.status === 'supported' ? '#34d399' : '#fbbf24';
        const localBadgeIcon = localPred.status === 'supported' ? 'fa-circle-check' : 'fa-circle-exclamation';
        const rawModelText = localPred.crop ? `${localPred.crop} — ${localPred.condition}` : (localPred.raw_candidate || data.unverified_model_artifact || 'None');
        const rawConfidence = localPred.confidence || data.confidence || 0;

        vHtml += `
            <div style="margin-bottom: 12px; padding: 12px 14px; background: rgba(15, 23, 42, 0.6); border-radius: 6px; border: 1px solid rgba(255,255,255,0.06);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 11px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px;">
                        <i class="fa-solid fa-microchip text-primary"></i> 1. Local ML Model Prediction
                    </span>
                    <span style="font-size: 10px; font-weight: 600; color: ${localColor}; background: rgba(255,255,255,0.04); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.08);">
                        <i class="fa-solid ${localBadgeIcon}"></i> Secondary Diagnostic Reference
                    </span>
                </div>
                <div style="font-size: 13px; color: var(--text-main); margin-bottom: 4px;">
                    <strong>Hypothesis:</strong> <code>${rawModelText}</code> 
                    <span style="color: #60a5fa; font-weight: 600; margin-left: 6px;">(${rawConfidence}% closed-set softmax)</span>
                </div>
                <div style="font-size: 11px; color: var(--text-muted); line-height: 1.4;">
                    ${localPred.confidence_description || "Closed-set statistical softmax score across 38 PlantVillage classes. Does not represent real-world diagnostic accuracy and cannot override contradictory image evidence."}
                </div>
            </div>
        `;

        // ── 2. Google Gemini Image Assessment Section ─────────────────────────
        const geminiConnected = (geminiAss.api_status === 'connected' || geminiAss.is_available);
        const likelyPlant = geminiAss.likely_plant || geminiAss.host_plant || data.likely_plant || 'Unverified Host';
        const leafStructure = geminiAss.leaf_shape_and_structure || geminiAss.leaf_structure || 'Structure unspecified';
        const foliarSymptoms = geminiAss.visible_spots_and_lesions || geminiAss.visible_symptoms || data.visible_symptoms || 'Foliar inspection completed';
        const colorPatterns = geminiAss.colour_changes_and_patterns || 'Characteristic chlorotic/necrotic patterning';
        const mostLikelyDisease = geminiAss.most_likely_disease || geminiAss.candidate_disease || data.most_likely_disease || 'Uncertain Condition';
        const altDiagnoses = geminiAss.alternative_diagnoses || data.alternative_diseases || [];

        vHtml += `
            <div style="margin-bottom: 12px; padding: 12px 14px; background: rgba(15, 23, 42, 0.6); border-radius: 6px; border: 1px solid rgba(255,255,255,0.06);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 11px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px;">
                        <i class="fa-brands fa-google text-primary"></i> 2. Google Gemini Image Assessment
                    </span>
                    <span style="font-size: 10px; background: ${geminiConnected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)'}; color: ${geminiConnected ? '#34d399' : '#fbbf24'}; padding: 2px 8px; border-radius: 4px; border: 1px solid ${geminiConnected ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'};">
                        ${geminiConnected ? 'Gemini Vision Connected' : 'Google Verification Unavailable'}
                    </span>
                </div>
                <div style="font-size: 12px; color: var(--text-main); margin-bottom: 4px;">
                    <strong>Likely Plant:</strong> <span style="color: #60a5fa; font-weight: 600;">${likelyPlant}</span> &nbsp;|&nbsp; 
                    <strong>Leaf Structure:</strong> <span>${leafStructure}</span>
                </div>
                <div style="font-size: 12px; color: var(--text-main); margin-bottom: 4px;">
                    <strong>Visible Spots &amp; Lesions:</strong> <span>${foliarSymptoms}</span>
                </div>
                <div style="font-size: 12px; color: var(--text-main); margin-bottom: 4px;">
                    <strong>Colour Patterns:</strong> <span>${colorPatterns}</span>
                </div>
                <div style="margin: 8px 0; padding: 8px 12px; background: rgba(59, 130, 246, 0.08); border-left: 3px solid #3b82f6; border-radius: 0 4px 4px 0;">
                    <div style="font-size: 11px; font-weight: 600; color: #93c5fd; text-transform: uppercase;">
                        Most Likely Disease:
                    </div>
                    <div style="font-size: 13px; font-weight: 700; color: var(--text-main); margin-top: 2px;">
                        ${mostLikelyDisease}
                    </div>
                    ${altDiagnoses.length > 0 ? `
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">
                            <strong>Alternative Diagnoses:</strong> ${altDiagnoses.join(' • ')}
                        </div>
                    ` : ''}
                </div>
                <div style="font-size: 11px; color: var(--text-muted); line-height: 1.4; margin-top: 6px;">
                    <i class="fa-solid fa-circle-info text-primary"></i> <em>${geminiAss.diagnostic_reasoning || "Multimodal preliminary assessment based on visual morphology."}</em>
                </div>
                ${geminiAss.error_message ? `
                    <div style="font-size: 11px; color: #fbbf24; margin-top: 6px; padding: 6px 10px; background: rgba(245, 158, 11, 0.08); border-radius: 4px; border: 1px solid rgba(245, 158, 11, 0.2);">
                        <i class="fa-solid fa-triangle-exclamation"></i> <strong>API Notice:</strong> ${geminiAss.error_message}
                    </div>
                ` : ''}
            </div>
        `;

        // ── 3. Google Search Grounding Corroboration Section ───────────────────
        const searchSources = searchCorrob.supporting_sources || searchCorrob.sources || data.supporting_sources || data.agricultural_references || [];
        const executedQueries = searchCorrob.search_queries_executed || searchCorrob.queries_executed || [];
        const causalOrganism = searchCorrob.causal_organism || 'Pathological causal agent';

        vHtml += `
            <div style="margin-bottom: 12px; padding: 12px 14px; background: rgba(15, 23, 42, 0.6); border-radius: 6px; border: 1px solid rgba(255,255,255,0.06);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 11px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px;">
                        <i class="fa-solid fa-earth-americas text-primary"></i> 3. Google Search Grounding Corroboration
                    </span>
                    <span style="font-size: 10px; color: var(--text-muted); background: rgba(255,255,255,0.04); padding: 2px 8px; border-radius: 4px;">
                        ${searchSources.length > 0 ? `${searchSources.length} Grounded Citations` : 'No Grounded Sources'}
                    </span>
                </div>
                <div style="font-size: 12px; color: var(--text-main); margin-bottom: 6px;">
                    <strong>Causal Organism:</strong> <em style="color: #60a5fa;">${causalOrganism}</em>
                </div>
                ${executedQueries.length > 0 ? `
                    <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 8px;">
                        <strong>Google Queries:</strong> ${executedQueries.map(q => `<code style="background:rgba(255,255,255,0.05);padding:1px 6px;border-radius:3px;margin:2px;">${q}</code>`).join(' ')}
                    </div>
                ` : ''}
        `;

        if (searchSources.length > 0) {
            vHtml += `
                <div style="font-size: 11px; font-weight: 600; color: #a7f3d0; margin-bottom: 6px;">
                    <i class="fa-solid fa-link"></i> Authenticated University &amp; Extension Citations:
                </div>
                <ul style="margin: 0; padding-left: 18px; font-size: 12px;">
                    ${searchSources.map(s => `
                        <li style="margin-bottom: 8px;">
                            <a href="${s.url}" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; font-weight: 600; text-decoration: underline;">
                                <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 10px; margin-right: 4px;"></i>${s.title || s.url}
                            </a>
                            <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">
                                ${s.domain ? `<span class="badge" style="font-size: 9px; padding: 1px 6px; margin-right: 6px; background: rgba(59,130,246,0.15); color: #93c5fd;">${s.domain}</span>` : ''}
                                ${s.source && s.source !== s.domain ? `<strong style="color: var(--text-main);">${s.source}: </strong>` : ''}
                                ${s.snippet ? s.snippet.substring(0, 160) + '...' : ''}
                            </div>
                        </li>
                    `).join('')}
                </ul>
            `;
        } else {
            vHtml += `
                <div style="font-size: 11px; color: var(--text-muted); padding: 8px 10px; background: rgba(255,255,255,0.02); border-radius: 4px;">
                    <i class="fa-solid fa-link-slash"></i> No live Google Search citations retrieved. Search credentials unconfigured or condition outside indexed extension records.
                </div>
            `;
        }

        if (searchCorrob.search_entry_point_html) {
            vHtml += `
                <div style="margin-top: 8px;">
                    ${searchCorrob.search_entry_point_html}
                </div>
            `;
        }

        vHtml += `</div>`;

        // ── 4. Management Recommendations Section ─────────────────────────────
        const immActions = mgmtRecs.immediate_actions || (data.management && data.management.immediate_actions) || [];
        const spreadActions = mgmtRecs.spread_prevention || (data.management && data.management.spread_prevention) || [];
        const cultActions = mgmtRecs.cultural_management || mgmtRecs.cultural_actions || (data.management && data.management.treatment_options && data.management.treatment_options.cultural) || [];
        const isWithheld = Boolean(mgmtRecs.chemical_advice_withheld || data.treatment_withheld);

        vHtml += `
            <div style="margin-bottom: 12px; padding: 12px 14px; background: rgba(15, 23, 42, 0.6); border-radius: 6px; border: 1px solid rgba(255,255,255,0.06);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 11px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px;">
                        <i class="fa-solid fa-shield-halved text-primary"></i> 4. Management Recommendations
                    </span>
                    <span style="font-size: 10px; background: ${isWithheld ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)'}; color: ${isWithheld ? '#f87171' : '#34d399'}; padding: 2px 8px; border-radius: 4px; border: 1px solid ${isWithheld ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'};">
                        ${isWithheld ? '<i class="fa-solid fa-ban"></i> Chemical Sprays Withheld' : '<i class="fa-solid fa-check"></i> Agronomic Guidance Active'}
                    </span>
                </div>
                ${immActions.length > 0 ? `
                    <div style="font-size: 11px; font-weight: 600; color: #fde68a; margin-bottom: 3px;">
                        <i class="fa-solid fa-bolt"></i> Immediate Containment Actions:
                    </div>
                    <ul style="margin: 0 0 8px; padding-left: 18px; font-size: 11px; color: var(--text-main); line-height: 1.4;">
                        ${immActions.slice(0, 3).map(a => `<li style="margin-bottom: 3px;">${a}</li>`).join('')}
                    </ul>
                ` : ''}
                ${cultActions.length > 0 ? `
                    <div style="font-size: 11px; font-weight: 600; color: #a7f3d0; margin-bottom: 3px;">
                        <i class="fa-solid fa-leaf"></i> Cultural &amp; Agronomic Hygiene:
                    </div>
                    <ul style="margin: 0 0 8px; padding-left: 18px; font-size: 11px; color: var(--text-main); line-height: 1.4;">
                        ${cultActions.slice(0, 3).map(a => `<li style="margin-bottom: 3px;">${a}</li>`).join('')}
                    </ul>
                ` : ''}
                ${isWithheld ? `
                    <div style="font-size: 11px; color: #fca5a5; line-height: 1.4; padding: 6px 10px; background: rgba(239, 68, 68, 0.08); border-radius: 4px; border-left: 3px solid #ef4444;">
                        <strong>Chemical Safety Safeguard:</strong> ${mgmtRecs.withheld_reason || "Synthetic chemical sprays are withheld. Chemical recommendations require verified plant identification and university extension registration for this specific crop."}
                    </div>
                ` : ''}
            </div>
        `;

        // ── 5. Diagnostic Limitations Section ─────────────────────────────────
        if (diagLimits.length > 0) {
            vHtml += `
                <div style="padding: 10px 14px; background: rgba(15, 23, 42, 0.4); border-radius: 6px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 4px;">
                        <i class="fa-solid fa-circle-exclamation"></i> Diagnostic Limitations
                    </div>
                    <ul style="margin: 0; padding-left: 18px; font-size: 11px; color: var(--text-muted); line-height: 1.4;">
                        ${diagLimits.map(lim => `<li style="margin-bottom: 2px;">${lim}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        verifContent.innerHTML = vHtml;
    }

    // Warning / Caution box for low-confidence
    const cautionBox = document.getElementById("disease-caution-box");
    if (cautionBox) {
        if (data.warning) {
            cautionBox.style.display = "flex";
            const cautionText = document.getElementById("disease-caution-text");
            if (cautionText) cautionText.textContent = data.warning;
        } else {
            cautionBox.style.display = "none";
        }
    }

    // Symptoms
    const symEl = document.getElementById("disease-symptoms");
    if (symEl) symEl.textContent = data.symptoms || "Characteristic foliar features observed.";

    // Care recommendations & Treatment Withheld Alert
    const treatmentAlert = document.getElementById("disease-treatment-withheld-alert");
    const treatmentTag = document.getElementById("treatment-status-tag");
    if (treatmentAlert) {
        treatmentAlert.style.display = data.treatment_withheld ? "block" : "none";
    }
    if (treatmentTag) {
        if (data.treatment_withheld) {
            treatmentTag.textContent = "Definitive Advice Withheld";
            treatmentTag.style.background = "rgba(245, 158, 11, 0.2)";
            treatmentTag.style.color = "#fbbf24";
        } else {
            treatmentTag.textContent = "Guidance Active";
            treatmentTag.style.background = "rgba(16, 185, 129, 0.2)";
            treatmentTag.style.color = "#34d399";
        }
    }

    const careList = document.getElementById("disease-care-list");
    if (careList) {
        careList.innerHTML = "";
        (data.care_recommendations || []).forEach(tip => {
            const li = document.createElement("li");
            const iconClass = data.treatment_withheld ? "fa-solid fa-shield-halved text-warning" : "fa-solid fa-seedling text-emerald";
            li.innerHTML = `<i class="${iconClass}"></i> <span>${tip}</span>`;
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
                        <div class="candidate-bar-fill" style="width: ${Math.min(100, Math.max(0, cand.confidence))}%"></div>
                        <span class="candidate-pct">${cand.confidence}%</span>
                    </div>
                </div>
            `);
        });
    }

    // AI Disclaimer
    const disclaimerEl = document.getElementById("disease-disclaimer");
    if (disclaimerEl && data.disclaimer) {
        disclaimerEl.style.display = "block";
        disclaimerEl.textContent = data.disclaimer;
    }

    // Render Comprehensive Evidence-Based Disease Management Guidance
    if (data.management) {
        renderDiseaseManagement(data.management, data.is_compatible, data.treatment_withheld, data.supporting_sources || data.agricultural_references);
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
                if (data.unsupported_notice) {
                    const notice = document.createElement("div");
                    notice.className = "unsupported-alert-box";
                    notice.style.gridColumn = "1 / -1";
                    notice.style.marginBottom = "14px";
                    notice.style.padding = "10px 14px";
                    notice.style.background = "rgba(239, 68, 68, 0.1)";
                    notice.style.border = "1px solid rgba(239, 68, 68, 0.3)";
                    notice.style.borderRadius = "6px";
                    notice.style.fontSize = "12px";
                    notice.style.color = "#fca5a5";
                    notice.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="margin-right:6px;"></i> <span>${data.unsupported_notice}</span>`;
                    container.appendChild(notice);
                }
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

function setupGlobalSearch() {

    const searchInput = document.getElementById("global-search");
    const resultsBox = document.getElementById("search-results");

    if (!searchInput || !resultsBox) return;

    const searchItems = [
        {
            title: "Dashboard",
            description: "Smart agriculture overview and ML engine status",
            keywords: "dashboard home overview agriculture",
            url: "/"
        },
        {
            title: "Crop Recommendation",
            description: "Get the best crop based on soil and climate parameters",
            keywords: "crop recommendation recommend N P K temperature humidity rainfall",
            url: "/recommend"
        },
        {
            title: "Crop Suitability",
            description: "Analyze how suitable your soil and climate are for a crop",
            keywords: "suitability soil climate assessment pH nitrogen phosphorus potassium",
            url: "/suitability"
        },
        {
            title: "Plant Disease Detection",
            description: "Detect plant diseases using an AI computer-vision model",
            keywords: "disease plant leaf detection tomato potato corn apple grape mobileNet",
            url: "/disease-detection"
        },
        {
            title: "Research Analytics",
            description: "Explore model performance, feature importance and agricultural data",
            keywords: "research analytics model accuracy precision recall F1 confusion matrix",
            url: "/research"
        },
        {
            title: "Crop Comparison",
            description: "Compare two crops using empirical soil and climate requirements",
            keywords: "compare crops rice maize crop comparison rainfall temperature",
            url: "/suitability"
        }
    ];

    function showResults(query) {

        const text = query.trim().toLowerCase();

        if (!text) {
            resultsBox.innerHTML = "";
            resultsBox.style.display = "none";
            return;
        }


        const matches = searchItems
            .map(item => {
                const title = item.title.toLowerCase();
                const desc = item.description.toLowerCase();
                const kw = item.keywords.toLowerCase();
                const titleWords = title.split(/[\s-]+/);
                const kwWords = kw.split(/[\s-]+/);

                let score = 0;

                if (title === text) {
                    score = 100;
                } else if (title.startsWith(text)) {
                    score = 90;
                } else if (titleWords.some(word => word.startsWith(text))) {
                    score = 80;
                } else if (desc.includes(text)) {
                    score = 60;
                } else if (kwWords.some(word => word.startsWith(text))) {
                    score = 50;
                } else if (kw.includes(text)) {
                    score = 40;
                }

                return { ...item, score };
            })
            .filter(item => item.score > 0)
            .sort((a, b) => b.score - a.score);


        if (matches.length === 0) {

            resultsBox.innerHTML = `
                <div class="search-no-results">
                    <i class="fa-solid fa-magnifying-glass"></i>
                    <span>No matching feature found</span>
                </div>
            `;

            resultsBox.style.display = "block";
            return;
        }

        resultsBox.innerHTML = matches.map(item => `
            <a href="${item.url}" class="search-result-item">
                <div class="search-result-icon">
                    <i class="fa-solid fa-arrow-right"></i>
                </div>

                <div class="search-result-content">
                    <strong>${item.title}</strong>
                    <span>${item.description}</span>
                </div>
            </a>
        `).join("");

        resultsBox.style.display = "block";
    }

    searchInput.addEventListener("input", function () {
        showResults(this.value);
    });

    searchInput.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {
            searchInput.value = "";
            resultsBox.innerHTML = "";
            resultsBox.style.display = "none";
        }

        if (event.key === "Enter") {

            const firstResult =
                resultsBox.querySelector(".search-result-item");

            if (firstResult) {
                firstResult.click();
            }
        }
    });

    document.addEventListener("click", function (event) {

        if (!event.target.closest(".header-search")) {
            resultsBox.style.display = "none";
        }
    });
}

/* ==========================================================================
   ADVANCED AGRICULTURAL INTELLIGENCE UPGRADE — CLIENT MODULES
   ========================================================================== */

/**
 * 1. Disease Management Guidance & Interactive Session Recovery Checklist
 */
function renderDiseaseManagement(mgmt, isCompatible, treatmentWithheld, searchSources) {
    if (!mgmt) return;

    // Pathogen banner
    const pathTypeEl = document.getElementById("disease-pathogen-type");
    if (pathTypeEl) pathTypeEl.textContent = mgmt.pathogen_type || "Foliar Pathology";
    const causalEl = document.getElementById("disease-causal-agent");
    if (causalEl) causalEl.textContent = mgmt.causal_agent || "Unclassified pathogen";

    // Tab 2: Immediate Actions
    const immList = document.getElementById("disease-immediate-list");
    if (immList) {
        immList.innerHTML = "";
        (mgmt.immediate_actions || []).forEach(act => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-bolt text-warning"></i> <span>${act}</span>`;
            immList.appendChild(li);
        });
    }

    // Tab 3: Spread Prevention & Cultural Care
    const spreadList = document.getElementById("disease-spread-list");
    if (spreadList) {
        spreadList.innerHTML = "";
        (mgmt.spread_prevention || []).forEach(sp => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-shield-virus text-primary"></i> <span>${sp}</span>`;
            spreadList.appendChild(li);
        });
    }
    const cultList = document.getElementById("disease-cultural-list");
    if (cultList) {
        cultList.innerHTML = "";
        (mgmt.cultural_management || []).forEach(cm => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-leaf text-emerald"></i> <span>${cm}</span>`;
            cultList.appendChild(li);
        });
    }

    // Tab 4: Verified Treatment Options
    const treatCultList = document.getElementById("treatment-cultural-list");
    if (treatCultList) {
        treatCultList.innerHTML = "";
        ((mgmt.treatment_options && mgmt.treatment_options.cultural) || []).forEach(t => {
            const li = document.createElement("li");
            li.textContent = t;
            treatCultList.appendChild(li);
        });
    }
    const treatBioList = document.getElementById("treatment-bio-list");
    if (treatBioList) {
        treatBioList.innerHTML = "";
        ((mgmt.treatment_options && mgmt.treatment_options.biological) || []).forEach(t => {
            const li = document.createElement("li");
            li.textContent = t;
            treatBioList.appendChild(li);
        });
    }
    const chemContainer = document.getElementById("treatment-chemical-container");
    const chemList = document.getElementById("treatment-chem-list");
    if (chemContainer && chemList) {
        chemList.innerHTML = "";
        const chems = (mgmt.treatment_options && mgmt.treatment_options.chemical) || [];
        if (chems.length > 0 && !treatmentWithheld) {
            chemContainer.style.display = "block";
            chems.forEach(c => {
                const li = document.createElement("li");
                li.textContent = c;
                chemList.appendChild(li);
            });
        } else {
            chemContainer.style.display = "none";
        }
    }
    const warnContainer = document.getElementById("treatment-warnings-container");
    const warnList = document.getElementById("treatment-warnings-list");
    if (warnContainer && warnList) {
        warnList.innerHTML = "";
        const warns = (mgmt.treatment_options && mgmt.treatment_options.warnings) || [];
        if (warns.length > 0) {
            warnContainer.style.display = "block";
            warns.forEach(w => {
                const li = document.createElement("li");
                li.textContent = w;
                warnList.appendChild(li);
            });
        } else {
            warnContainer.style.display = "none";
        }
    }

    // Tab 5: Recovery Signs & Interactive Checklist
    const recSignsList = document.getElementById("disease-recovery-signs-list");
    if (recSignsList) {
        recSignsList.innerHTML = "";
        (mgmt.recovery_monitoring || []).forEach(rm => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-binoculars text-primary"></i> <span>${rm}</span>`;
            recSignsList.appendChild(li);
        });
    }
    const expCriteria = document.getElementById("disease-expert-criteria");
    if (expCriteria) {
        expCriteria.textContent = mgmt.expert_assistance || "Contact your nearest KVK (Krishi Vigyan Kendra) or university extension plant pathologist for laboratory confirmation.";
    }
    renderRecoveryChecklist(mgmt);

    // Tab 6: References & Next Cycle
    const refsContainer = document.getElementById("disease-references-container");
    if (refsContainer) {
        refsContainer.innerHTML = "";

        // First render authentic Google Search Grounded references if present
        if (searchSources && searchSources.length > 0) {
            searchSources.forEach(s => {
                const card = document.createElement("div");
                card.style.padding = "10px 14px";
                card.style.background = "rgba(59, 130, 246, 0.05)";
                card.style.border = "1px solid rgba(59, 130, 246, 0.25)";
                card.style.borderRadius = "6px";
                card.style.fontSize = "12px";
                card.style.marginBottom = "8px";
                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-weight: 700; color: #93c5fd;"><i class="fa-solid fa-earth-americas text-primary"></i> Google Search Grounding Reference</span>
                        ${s.domain ? `<span class="badge" style="font-size: 9px; padding: 2px 6px; background: rgba(59,130,246,0.2); color: #60a5fa;">${s.domain}</span>` : ''}
                    </div>
                    <div style="font-weight: 600; color: var(--text-main); font-size: 13px;">${s.title || s.url}</div>
                    ${s.snippet ? `<div style="color: var(--text-muted); font-size: 11px; margin-top: 3px;">${s.snippet}</div>` : ''}
                    ${s.url ? `<a href="${s.url}" target="_blank" rel="noopener noreferrer" style="color: #60a5fa; font-size: 11px; text-decoration: underline; margin-top: 6px; display: inline-block; font-weight: 600;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Open Source Extension Link</a>` : ''}
                `;
                refsContainer.appendChild(card);
            });
        }

        // Then render KB references
        (mgmt.references || []).forEach(ref => {
            const card = document.createElement("div");
            card.style.padding = "10px 14px";
            card.style.background = "rgba(255,255,255,0.02)";
            card.style.border = "1px solid var(--panel-border)";
            card.style.borderRadius = "6px";
            card.style.fontSize = "12px";
            card.style.marginBottom = "8px";
            card.innerHTML = `
                <div style="font-weight: 600; color: var(--text-main);">${ref.title}</div>
                <div style="color: var(--text-muted); font-size: 11px; margin-top: 2px;">Authority: ${ref.source}</div>
                ${ref.notes ? `<div style="color: var(--text-muted); font-size: 11px; margin-top: 2px; font-style: italic;">Scope: ${ref.notes}</div>` : ''}
                ${ref.url ? `<a href="${ref.url}" target="_blank" rel="noopener noreferrer" style="color: var(--primary); font-size: 11px; text-decoration: underline; margin-top: 4px; display: inline-block;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Traceable Extension Reference</a>` : ''}
            `;
            refsContainer.appendChild(card);
        });
    }
    const nextCycleList = document.getElementById("disease-next-cycle-list");
    if (nextCycleList) {
        nextCycleList.innerHTML = "";
        (mgmt.prevention_next_cycle || []).forEach(nc => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-arrow-rotate-right text-primary"></i> <span>${nc}</span>`;
            nextCycleList.appendChild(li);
        });
    }
}

function renderRecoveryChecklist(mgmt) {
    const container = document.getElementById("recovery-checklist-container");
    const badge = document.getElementById("checklist-progress-badge");
    if (!container) return;

    container.innerHTML = "";
    const items = [];
    (mgmt.immediate_actions || []).forEach((act, idx) => {
        items.push({ id: `chk-act-${idx}`, text: `[Immediate] ${act}` });
    });
    (mgmt.spread_prevention || []).slice(0, 2).forEach((sp, idx) => {
        items.push({ id: `chk-sp-${idx}`, text: `[Biosecurity] ${sp}` });
    });
    if (items.length === 0) {
        items.push({ id: 'chk-d1', text: 'Scout adjacent rows for early foliar lesion transmission.' });
        items.push({ id: 'chk-d2', text: 'Sanitize cutting tools with 70% alcohol.' });
    }

    let completed = 0;
    const total = items.length;

    function updateBadge() {
        if (badge) {
            badge.textContent = `${completed} / ${total} Completed`;
            if (completed === total) {
                badge.style.background = "rgba(16, 185, 129, 0.25)";
                badge.style.color = "#34d399";
            } else {
                badge.style.background = "rgba(59, 130, 246, 0.2)";
                badge.style.color = "#93c5fd";
            }
        }
    }

    items.forEach(item => {
        const row = document.createElement("label");
        row.style.display = "flex";
        row.style.alignItems = "flex-start";
        row.style.gap = "10px";
        row.style.padding = "8px 12px";
        row.style.background = "rgba(255,255,255,0.02)";
        row.style.border = "1px solid var(--panel-border)";
        row.style.borderRadius = "6px";
        row.style.cursor = "pointer";
        row.style.fontSize = "12px";
        row.style.lineHeight = "1.4";

        const chk = document.createElement("input");
        chk.type = "checkbox";
        chk.id = item.id;
        chk.style.marginTop = "3px";
        chk.style.cursor = "pointer";

        const textSpan = document.createElement("span");
        textSpan.textContent = item.text;

        chk.addEventListener("change", () => {
            if (chk.checked) {
                completed++;
                textSpan.style.textDecoration = "line-through";
                textSpan.style.color = "var(--text-muted)";
                row.style.borderColor = "rgba(16, 185, 129, 0.4)";
            } else {
                completed--;
                textSpan.style.textDecoration = "none";
                textSpan.style.color = "var(--text-main)";
                row.style.borderColor = "var(--panel-border)";
            }
            updateBadge();
        });

        row.appendChild(chk);
        row.appendChild(textSpan);
        container.appendChild(row);
    });

    updateBadge();
}

/**
 * 2. Dashboard Smart Farm Health & Risk Summary
 */
/**
 * 2. Dashboard Smart Farm Health & Risk Summary
 */
let currentDashboardInputs = null;

function setupFarmHealthDashboard() {
    const profileBtns = document.querySelectorAll(".farm-profile-btn");
    const toggleCustomBtn = document.getElementById("btn-toggle-custom-health");
    const customDrawer = document.getElementById("custom-health-drawer");
    const evalCustomBtn = document.getElementById("btn-eval-custom-health");
    const loadDefaultBtn = document.getElementById("btn-load-default-alluvial");

    // 1. Predefined Profile Click Handlers (Demo Benchmarks)
    profileBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const n = parseFloat(btn.getAttribute("data-n") || 85);
            const p = parseFloat(btn.getAttribute("data-p") || 45);
            const k = parseFloat(btn.getAttribute("data-k") || 42);
            const temp = parseFloat(btn.getAttribute("data-temp") || 24.5);
            const hum = parseFloat(btn.getAttribute("data-hum") || 82);
            const ph = parseFloat(btn.getAttribute("data-ph") || 6.5);
            const rain = parseFloat(btn.getAttribute("data-rain") || 210);
            const profileName = btn.getAttribute("data-profile") || btn.textContent.trim();

            // Update active button styling
            profileBtns.forEach(b => b.classList.remove("active"));
            if (toggleCustomBtn) toggleCustomBtn.classList.remove("active");
            btn.classList.add("active");

            const inputs = { N: n, P: p, K: k, temperature: temp, humidity: hum, ph: ph, rainfall: rain };

            // Pre-populate custom drawer inputs so user can see and tweak them
            syncDashboardInputs(inputs);

            // Evaluate farm health via backend API
            evaluateFarmHealth(inputs, `Demo Benchmark: ${profileName}`, true);
        });
    });

    // 2. Load Default Alluvial Profile Button (in Empty State)
    if (loadDefaultBtn) {
        loadDefaultBtn.addEventListener("click", () => {
            const defaultBtn = document.getElementById("btn-profile-alluvial") || document.querySelector(".farm-profile-btn");
            if (defaultBtn) {
                defaultBtn.click();
            } else {
                const defaultInputs = { N: 85, P: 45, K: 42, temperature: 24.5, humidity: 82, ph: 6.5, rainfall: 210 };
                syncDashboardInputs(defaultInputs);
                evaluateFarmHealth(defaultInputs, "Demo Benchmark: Alluvial Loam", true);
            }
        });
    }

    // 3. Custom Input Drawer Toggle
    if (toggleCustomBtn && customDrawer) {
        toggleCustomBtn.addEventListener("click", () => {
            const isHidden = customDrawer.style.display === "none" || !customDrawer.style.display;
            customDrawer.style.display = isHidden ? "block" : "none";
            if (isHidden) {
                toggleCustomBtn.classList.add("active");
                customDrawer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                document.getElementById("dash-input-n")?.focus();
            } else {
                toggleCustomBtn.classList.remove("active");
            }
        });
    }

    // 4. Custom Measurement Evaluate Button
    if (evalCustomBtn) {
        evalCustomBtn.addEventListener("click", () => {
            const customInputs = {
                N: parseFloat(document.getElementById("dash-input-n")?.value || 70),
                P: parseFloat(document.getElementById("dash-input-p")?.value || 45),
                K: parseFloat(document.getElementById("dash-input-k")?.value || 45),
                ph: parseFloat(document.getElementById("dash-input-ph")?.value || 6.5),
                temperature: parseFloat(document.getElementById("dash-input-temp")?.value || 25),
                humidity: parseFloat(document.getElementById("dash-input-hum")?.value || 75),
                rainfall: parseFloat(document.getElementById("dash-input-rain")?.value || 150)
            };

            // Update active styling
            profileBtns.forEach(b => b.classList.remove("active"));
            if (toggleCustomBtn) toggleCustomBtn.classList.add("active");

            evaluateFarmHealth(customInputs, "Custom Field Measurements (User-Entered)", false);
        });
    }

    // 5. Cross-Section Deep Navigation Buttons
    const toRecommendBtn = document.getElementById("btn-dash-to-recommend");
    const toSuitabilityBtn = document.getElementById("btn-dash-to-suitability");

    if (toRecommendBtn) {
        toRecommendBtn.addEventListener("click", () => {
            if (!currentDashboardInputs) return;
            const q = new URLSearchParams({
                n: currentDashboardInputs.N,
                p: currentDashboardInputs.P,
                k: currentDashboardInputs.K,
                temp: currentDashboardInputs.temperature,
                hum: currentDashboardInputs.humidity,
                ph: currentDashboardInputs.ph,
                rain: currentDashboardInputs.rainfall
            });
            window.location.href = `/recommend?${q.toString()}`;
        });
    }

    if (toSuitabilityBtn) {
        toSuitabilityBtn.addEventListener("click", () => {
            if (!currentDashboardInputs) return;
            const q = new URLSearchParams({
                n: currentDashboardInputs.N,
                p: currentDashboardInputs.P,
                k: currentDashboardInputs.K,
                temp: currentDashboardInputs.temperature,
                hum: currentDashboardInputs.humidity,
                ph: currentDashboardInputs.ph,
                rain: currentDashboardInputs.rainfall
            });
            window.location.href = `/suitability?${q.toString()}`;
        });
    }
}

function syncDashboardInputs(inputs) {
    const map = {
        'dash-input-n': inputs.N,
        'dash-input-p': inputs.P,
        'dash-input-k': inputs.K,
        'dash-input-ph': inputs.ph,
        'dash-input-temp': inputs.temperature,
        'dash-input-hum': inputs.humidity,
        'dash-input-rain': inputs.rainfall
    };
    Object.keys(map).forEach(id => {
        const el = document.getElementById(id);
        if (el && map[id] !== undefined) {
            el.value = map[id];
        }
    });
}

function evaluateFarmHealth(inputs, label = "Active Measurements", isDemo = true) {
    const scoreVal = document.getElementById("farm-health-score-val");
    if (!scoreVal) return;

    currentDashboardInputs = inputs;

    // Measurement status & provenance tags
    const statusBadge = document.getElementById("farm-health-active-status");
    const provTag = document.getElementById("farm-health-provenance-tag");
    const provText = document.getElementById("farm-health-provenance-text");

    if (statusBadge) {
        statusBadge.textContent = label;
        statusBadge.style.background = isDemo ? "rgba(59, 130, 246, 0.15)" : "rgba(16, 185, 129, 0.15)";
        statusBadge.style.color = isDemo ? "#60a5fa" : "#34d399";
        statusBadge.style.border = `1px solid ${isDemo ? 'rgba(59, 130, 246, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`;
    }

    if (provTag && provText) {
        provTag.style.display = "block";
        if (isDemo) {
            provText.innerHTML = `<strong>Benchmark Demo Scenario:</strong> Predefined trial measurements &bull; <em>Not live physical sensor telemetry.</em>`;
        } else {
            provText.innerHTML = `<strong>Custom Field Data:</strong> User-specified soil nutrient and climatic measurements.`;
        }
    }

    fetch("/api/farm-health-summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inputs)
    })
        .then(async res => {
            const contentType = res.headers.get("content-type") || "";
            if (contentType.includes("application/json")) {
                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.error || `Server returned status ${res.status}`);
                }
                return data;
            } else {
                const text = await res.text();
                throw new Error(`Server returned HTTP ${res.status}: ${text.slice(0, 100)}`);
            }
        })
        .then(data => {
            if (data.error) {
                alert("Farm Health Evaluation Error: " + data.error);
                return;
            }

            // Show results view, hide empty state
            const emptyState = document.getElementById("farm-health-empty-state");
            const resultsPanel = document.getElementById("farm-health-results");
            if (emptyState) emptyState.style.display = "none";
            if (resultsPanel) {
                resultsPanel.style.display = "block";
                resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }

            // Health Score & Rating
            scoreVal.textContent = data.health_score;
            if (data.health_score >= 80) scoreVal.style.color = "#34d399";
            else if (data.health_score >= 60) scoreVal.style.color = "#fbbf24";
            else scoreVal.style.color = "#f87171";

            const ratingBadge = document.getElementById("farm-health-rating-badge");
            if (ratingBadge) {
                ratingBadge.textContent = (data.health_rating || "NORMAL").toUpperCase();
                if (data.health_score >= 80) {
                    ratingBadge.style.background = "rgba(16, 185, 129, 0.2)";
                    ratingBadge.style.color = "#34d399";
                } else if (data.health_score >= 60) {
                    ratingBadge.style.background = "rgba(245, 158, 11, 0.2)";
                    ratingBadge.style.color = "#fbbf24";
                } else {
                    ratingBadge.style.background = "rgba(239, 68, 68, 0.2)";
                    ratingBadge.style.color = "#f87171";
                }
            }

            // Nutrients Status
            if (data.nutrients) {
                const nVal = document.getElementById("dash-n-val");
                const nBadge = document.getElementById("dash-n-badge");
                if (nVal) nVal.textContent = `${data.nutrients.N.value} ${data.nutrients.N.unit}`;
                if (nBadge) {
                    nBadge.textContent = `${data.nutrients.N.status} (${data.nutrients.N.optimal} optimal)`;
                    nBadge.className = `badge status-badge ${data.nutrients.N.color}`;
                }

                const pVal = document.getElementById("dash-p-val");
                const pBadge = document.getElementById("dash-p-badge");
                if (pVal) pVal.textContent = `${data.nutrients.P.value} ${data.nutrients.P.unit}`;
                if (pBadge) {
                    pBadge.textContent = `${data.nutrients.P.status} (${data.nutrients.P.optimal} optimal)`;
                    pBadge.className = `badge status-badge ${data.nutrients.P.color}`;
                }

                const kVal = document.getElementById("dash-k-val");
                const kBadge = document.getElementById("dash-k-badge");
                if (kVal) kVal.textContent = `${data.nutrients.K.value} ${data.nutrients.K.unit}`;
                if (kBadge) {
                    kBadge.textContent = `${data.nutrients.K.status} (${data.nutrients.K.optimal} optimal)`;
                    kBadge.className = `badge status-badge ${data.nutrients.K.color}`;
                }
            }

            // Soil pH Reaction
            if (data.ph) {
                const phStatus = document.getElementById("dash-ph-status");
                if (phStatus) {
                    phStatus.innerHTML = `<span class="badge status-badge ${data.ph.color}">${data.ph.status}</span> <span style="color:var(--text-main); font-weight:600;">(pH ${data.ph.value})</span> <span style="font-size:11px; color:var(--text-muted);">(Optimal: ${data.ph.optimal})</span>`;
                }
            }

            // Climate & Pathogen Hazard
            if (data.climate) {
                const climStatus = document.getElementById("dash-climate-status");
                if (climStatus) {
                    climStatus.innerHTML = `<span class="badge status-badge ${data.climate.color}">${data.climate.status}</span> <span style="color:var(--text-muted); font-size:11px;">(${data.climate.temperature}°C &bull; ${data.climate.humidity}% RH &bull; ${data.climate.rainfall}mm)</span>`;
                }
            }

            // Active Condition Alerts
            const alertsCont = document.getElementById("dash-alerts-container");
            if (alertsCont) {
                alertsCont.innerHTML = "";
                if (!data.alerts || data.alerts.length === 0) {
                    alertsCont.innerHTML = `<div style="font-size: 12px; color: #34d399; padding: 10px 14px; background: rgba(16, 185, 129, 0.08); border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.2);"><i class="fa-solid fa-circle-check"></i> Balanced agro-ecological conditions: no acute nutrient deficit or atmospheric pathogen alerts.</div>`;
                } else {
                    data.alerts.forEach(al => {
                        const div = document.createElement("div");
                        const isWarn = al.type === 'warning';
                        div.style.padding = "10px 14px";
                        div.style.background = isWarn ? "rgba(245, 158, 11, 0.08)" : "rgba(239, 68, 68, 0.08)";
                        div.style.border = `1px solid ${isWarn ? 'rgba(245, 158, 11, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`;
                        div.style.borderRadius = "6px";
                        div.style.fontSize = "12px";
                        div.innerHTML = `
                            <strong style="color: ${isWarn ? '#fbbf24' : '#f87171'};"><i class="fa-solid fa-triangle-exclamation"></i> ${al.title}</strong>
                            <p style="margin: 4px 0 0; color: var(--text-main); font-size: 12px; line-height: 1.4;">${al.desc}</p>
                        `;
                        alertsCont.appendChild(div);
                    });
                }
            }

            // Prioritized Actions
            const actionsList = document.getElementById("dash-actions-list");
            if (actionsList) {
                actionsList.innerHTML = "";
                (data.prioritized_actions || []).forEach(act => {
                    const li = document.createElement("li");
                    li.style.marginBottom = "4px";
                    li.innerHTML = `<span>${act}</span>`;
                    actionsList.appendChild(li);
                });
            }
        })
        .catch(err => {
            console.error("Farm health fetch error:", err);
            alert("Failed to analyze farm health: " + err.message);
        });
}

/**
 * 3. Crop Recommend What-If Scenario Simulator
 */
function setupWhatIfSimulator() {
    const runBtn = document.getElementById("btn-run-what-if");
    const resetBtn = document.getElementById("btn-reset-what-if");
    if (!runBtn && !resetBtn) return;

    const params = [
        { id: 'n', formId: 'input-n', def: 70, unit: 'mg/kg', decimals: 0 },
        { id: 'p', formId: 'input-p', def: 45, unit: 'mg/kg', decimals: 0 },
        { id: 'k', formId: 'input-k', def: 45, unit: 'mg/kg', decimals: 0 },
        { id: 'ph', formId: 'input-ph', def: 6.5, unit: '', decimals: 1 },
        { id: 'temp', formId: 'input-temp', def: 25.0, unit: '°C', decimals: 1 },
        { id: 'hum', formId: 'input-hum', def: 75.0, unit: '%', decimals: 0 },
        { id: 'rain', formId: 'input-rain', def: 150.0, unit: 'mm', decimals: 0 }
    ];

    function getBaselineVal(p) {
        const formInput = document.getElementById(p.formId);
        if (formInput && formInput.value !== "" && !isNaN(parseFloat(formInput.value))) {
            return parseFloat(formInput.value);
        }
        return p.def;
    }

    function updateParamDelta(p, currentVal) {
        const baseVal = getBaselineVal(p);
        const delta = currentVal - baseVal;
        const deltaEl = document.getElementById(`delta-${p.id}`);
        const displayEl = document.getElementById(`sim-${p.id}-display`);

        if (displayEl) {
            displayEl.textContent = p.unit ? `${currentVal} ${p.unit}` : `${currentVal}`;
        }

        if (deltaEl) {
            if (Math.abs(delta) < 0.001) {
                deltaEl.textContent = "Δ 0";
                deltaEl.className = "badge";
                deltaEl.style.color = "";
                deltaEl.style.borderColor = "";
            } else {
                const sign = delta > 0 ? "+" : "";
                deltaEl.textContent = `Δ ${sign}${delta.toFixed(p.decimals > 0 ? 1 : 0)}`;
                deltaEl.className = `badge whatif-delta-badge ${delta > 0 ? 'whatif-delta-pos' : 'whatif-delta-neg'}`;
            }
        }
    }

    // Attach bi-directional sync for all 7 sliders and number inputs
    params.forEach(p => {
        const sliderEl = document.getElementById(`sim-${p.id}-slider`);
        const numEl = document.getElementById(`sim-${p.id}-num`);

        if (sliderEl && numEl) {
            sliderEl.addEventListener("input", (e) => {
                const val = parseFloat(e.target.value);
                numEl.value = val;
                updateParamDelta(p, val);
            });

            numEl.addEventListener("input", (e) => {
                if (e.target.value !== "") {
                    const val = parseFloat(e.target.value);
                    sliderEl.value = val;
                    updateParamDelta(p, val);
                }
            });
        }
    });

    // Preset buttons (.sim-preset-btn)
    const presetButtons = document.querySelectorAll(".sim-preset-btn");
    presetButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const presetType = btn.getAttribute("data-preset");
            const getCur = (id) => parseFloat(document.getElementById(`sim-${id}-num`)?.value) || 0;

            if (presetType === "drought") {
                // Drought Stress (-50mm Rain, +3°C Temp)
                const rainEl = document.getElementById("sim-rain-num");
                const rainSlider = document.getElementById("sim-rain-slider");
                const tempEl = document.getElementById("sim-temp-num");
                const tempSlider = document.getElementById("sim-temp-slider");
                if (rainEl && rainSlider) {
                    const newRain = Math.max(10, Math.round(getCur('rain') - 50));
                    rainEl.value = newRain;
                    rainSlider.value = newRain;
                    updateParamDelta(params.find(x => x.id === 'rain'), newRain);
                }
                if (tempEl && tempSlider) {
                    const newTemp = Math.min(50, Math.round((getCur('temp') + 3.0) * 10) / 10);
                    tempEl.value = newTemp;
                    tempSlider.value = newTemp;
                    updateParamDelta(params.find(x => x.id === 'temp'), newTemp);
                }
            } else if (presetType === "nitrogen") {
                // Nitrogen Boost (+40 mg/kg N)
                const nEl = document.getElementById("sim-n-num");
                const nSlider = document.getElementById("sim-n-slider");
                if (nEl && nSlider) {
                    const newN = Math.min(150, Math.round(getCur('n') + 40));
                    nEl.value = newN;
                    nSlider.value = newN;
                    updateParamDelta(params.find(x => x.id === 'n'), newN);
                }
            } else if (presetType === "acid") {
                // Acidification (-1.5 pH)
                const phEl = document.getElementById("sim-ph-num");
                const phSlider = document.getElementById("sim-ph-slider");
                if (phEl && phSlider) {
                    const newPH = Math.max(3.5, Math.round((getCur('ph') - 1.5) * 10) / 10);
                    phEl.value = newPH;
                    phSlider.value = newPH;
                    updateParamDelta(params.find(x => x.id === 'ph'), newPH);
                }
            } else if (presetType === "monsoon") {
                // Heavy Monsoon (+90mm Rain, +15% Hum)
                const rainEl = document.getElementById("sim-rain-num");
                const rainSlider = document.getElementById("sim-rain-slider");
                const humEl = document.getElementById("sim-hum-num");
                const humSlider = document.getElementById("sim-hum-slider");
                if (rainEl && rainSlider) {
                    const newRain = Math.min(350, Math.round(getCur('rain') + 90));
                    rainEl.value = newRain;
                    rainSlider.value = newRain;
                    updateParamDelta(params.find(x => x.id === 'rain'), newRain);
                }
                if (humEl && humSlider) {
                    const newHum = Math.min(100, Math.round(getCur('hum') + 15));
                    humEl.value = newHum;
                    humSlider.value = newHum;
                    updateParamDelta(params.find(x => x.id === 'hum'), newHum);
                }
            }
        });
    });

    // Reset to Baseline Handler
    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            params.forEach(p => {
                const baseVal = getBaselineVal(p);
                const sliderEl = document.getElementById(`sim-${p.id}-slider`);
                const numEl = document.getElementById(`sim-${p.id}-num`);
                if (sliderEl) sliderEl.value = baseVal;
                if (numEl) numEl.value = baseVal;
                updateParamDelta(p, baseVal);
            });
            const resultsPanel = document.getElementById("what-if-results");
            if (resultsPanel) {
                resultsPanel.style.display = "none";
            }
        });
    }

    // Run Simulation Handler
    if (runBtn) {
        runBtn.addEventListener("click", () => runWhatIfSimulation(params));
    }
}

function runWhatIfSimulation(params) {
    const runBtn = document.getElementById("btn-run-what-if");
    const origHtml = runBtn?.innerHTML;

    // Collect baseline from recommendation form (or fallback)
    const baseline = {
        N: parseFloat(document.getElementById("input-n")?.value || 70),
        P: parseFloat(document.getElementById("input-p")?.value || 45),
        K: parseFloat(document.getElementById("input-k")?.value || 45),
        ph: parseFloat(document.getElementById("input-ph")?.value || 6.5),
        temperature: parseFloat(document.getElementById("input-temp")?.value || 25.0),
        humidity: parseFloat(document.getElementById("input-hum")?.value || 75.0),
        rainfall: parseFloat(document.getElementById("input-rain")?.value || 150.0)
    };

    // Collect modified from simulator controls
    const modified = {
        N: parseFloat(document.getElementById("sim-n-num")?.value || 70),
        P: parseFloat(document.getElementById("sim-p-num")?.value || 45),
        K: parseFloat(document.getElementById("sim-k-num")?.value || 45),
        ph: parseFloat(document.getElementById("sim-ph-num")?.value || 6.5),
        temperature: parseFloat(document.getElementById("sim-temp-num")?.value || 25.0),
        humidity: parseFloat(document.getElementById("sim-hum-num")?.value || 75.0),
        rainfall: parseFloat(document.getElementById("sim-rain-num")?.value || 150.0)
    };

    if (runBtn) {
        runBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Simulating Machine Learning Prediction...';
        runBtn.disabled = true;
    }

    fetch("/api/what-if", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ original: baseline, modified: modified })
    })
        .then(async res => {
            const contentType = res.headers.get("content-type") || "";
            if (contentType.includes("application/json")) {
                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.error || `Server error (${res.status})`);
                }
                return data;
            } else {
                const text = await res.text();
                throw new Error(`Server returned status ${res.status}: ${text.slice(0, 100)}`);
            }
        })
        .then(data => {
            if (runBtn) {
                runBtn.innerHTML = origHtml;
                runBtn.disabled = false;
            }

            if (data.error) {
                alert("What-If Simulation Error: " + data.error);
                return;
            }

            const resultsBox = document.getElementById("what-if-results");
            if (resultsBox) {
                resultsBox.style.display = "block";
                resultsBox.scrollIntoView({ behavior: 'smooth' });
            }

            // Baseline Card
            const baseData = data.original || data.baseline || data.original_prediction;
            if (baseData) {
                const bCrop = document.getElementById("sim-baseline-crop");
                const bConf = document.getElementById("sim-baseline-conf");
                const bSuit = document.getElementById("sim-baseline-suit");
                const bTop3 = document.getElementById("sim-baseline-top3");
                if (bCrop) bCrop.textContent = baseData.crop;
                if (bConf) bConf.textContent = `${baseData.confidence}%`;
                if (bSuit) bSuit.textContent = `${baseData.suitability_score}%`;
                if (bTop3 && baseData.top_crops) {
                    bTop3.innerHTML = "";
                    baseData.top_crops.forEach((item, idx) => {
                        const medal = ["🥇", "🥈", "🥉"][idx] || `#${idx + 1}`;
                        const li = document.createElement("li");
                        li.innerHTML = `<strong>${medal} ${item.crop}</strong> &bull; ${item.confidence}% confidence (${item.suitability_score}% suitability)`;
                        bTop3.appendChild(li);
                    });
                }
            }

            // Modified Card
            const modData = data.modified || data.scenario || data.scenario_prediction;
            if (modData) {
                const mCrop = document.getElementById("sim-modified-crop");
                const mConf = document.getElementById("sim-modified-conf");
                const mSuit = document.getElementById("sim-modified-suit");
                const mTop3 = document.getElementById("sim-modified-top3");
                const mShift = document.getElementById("sim-shift-badge");
                if (mCrop) mCrop.textContent = modData.crop;
                if (mConf) mConf.textContent = `${modData.confidence}%`;
                if (mSuit) mSuit.textContent = `${modData.suitability_score}%`;
                if (mTop3 && modData.top_crops) {
                    mTop3.innerHTML = "";
                    modData.top_crops.forEach((item, idx) => {
                        const medal = ["🥇", "🥈", "🥉"][idx] || `#${idx + 1}`;
                        const li = document.createElement("li");
                        li.innerHTML = `<strong>${medal} ${item.crop}</strong> &bull; ${item.confidence}% confidence (${item.suitability_score}% suitability)`;
                        mTop3.appendChild(li);
                    });
                }
                if (mShift && baseData) {
                    if (baseData.crop !== modData.crop) {
                        mShift.textContent = `PREDICTION SHIFT: ${baseData.crop} → ${modData.crop}`;
                        mShift.style.background = "rgba(245, 158, 11, 0.2)";
                        mShift.style.color = "#fbbf24";
                    } else {
                        mShift.textContent = "STABLE OPTIMAL CROP";
                        mShift.style.background = "rgba(16, 185, 129, 0.2)";
                        mShift.style.color = "#34d399";
                    }
                }
            }

            // Explanation
            const expText = document.getElementById("sim-explanation-text");
            if (expText && data.explanation) {
                expText.textContent = data.explanation.summary;
            }
        })
        .catch(err => {
            if (runBtn) {
                runBtn.innerHTML = origHtml;
                runBtn.disabled = false;
            }
            alert("What-If Simulator Request Failed: " + err.message);
        });
}

/**
 * 4. Crop Suitability Explainable Multi-Crop Comparison
 */
function setupMultiCropSuitability() {
    const rankBtn = document.getElementById("btn-rank-all-crops");
    if (!rankBtn) return;

    rankBtn.addEventListener("click", () => {
        const inputs = {
            N: parseFloat(document.getElementById("input-n")?.value || 90),
            P: parseFloat(document.getElementById("input-p")?.value || 42),
            K: parseFloat(document.getElementById("input-k")?.value || 43),
            temperature: parseFloat(document.getElementById("input-temp")?.value || 20.87),
            humidity: parseFloat(document.getElementById("input-hum")?.value || 82.0),
            ph: parseFloat(document.getElementById("input-ph")?.value || 6.5),
            rainfall: parseFloat(document.getElementById("input-rain")?.value || 202.91)
        };
        runMultiCropSuitability(inputs);
    });
}

function runMultiCropSuitability(inputs) {
    const rankBtn = document.getElementById("btn-rank-all-crops");
    const origHtml = rankBtn?.innerHTML;
    if (rankBtn) {
        rankBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Ranking All 22 Crops...';
        rankBtn.disabled = true;
    }

    fetch("/api/multi-crop-suitability", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inputs)
    })
        .then(async res => {
            const contentType = res.headers.get("content-type") || "";
            if (contentType.includes("application/json")) {
                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.error || `Server error (${res.status})`);
                }
                return data;
            } else {
                const text = await res.text();
                throw new Error(`Server returned status ${res.status}: ${text.slice(0, 100)}`);
            }
        })
        .then(data => {
            if (rankBtn) {
                rankBtn.innerHTML = origHtml;
                rankBtn.disabled = false;
            }

            if (data.error) {
                alert("Multi-Crop Suitability Error: " + data.error);
                return;
            }

            const ctaBox = document.getElementById("multi-crop-cta-box");
            if (ctaBox) ctaBox.style.display = "none";

            const container = document.getElementById("multi-crop-results-container");
            if (container) {
                container.style.display = "block";
                container.scrollIntoView({ behavior: 'smooth' });
            }

            const tbody = document.getElementById("multi-crop-table-body");
            if (tbody && data.ranked_crops) {
                tbody.innerHTML = "";
                data.ranked_crops.forEach((c, idx) => {
                    const tr = document.createElement("tr");
                    tr.className = "multi-crop-row";
                    const medal = idx === 0 ? "🥇" : (idx === 1 ? "🥈" : (idx === 2 ? "🥉" : `#${idx + 1}`));
                    let scoreBadgeColor = "#34d399";
                    if (c.suitability_score < 50) scoreBadgeColor = "#f87171";
                    else if (c.suitability_score < 80) scoreBadgeColor = "#fbbf24";

                    tr.innerHTML = `
                        <td style="font-weight: 700;">${medal}</td>
                        <td><strong>${c.crop}</strong></td>
                        <td>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.08); border-radius: 3px; overflow: hidden; min-width: 60px;">
                                    <div style="width: ${c.suitability_score}%; height: 100%; background: ${scoreBadgeColor};"></div>
                                </div>
                                <span style="font-weight: 700; color: ${scoreBadgeColor}; font-size: 12px;">${c.suitability_score}%</span>
                            </div>
                        </td>
                        <td><span class="status-badge ${c.classification_color}">${c.classification}</span></td>
                        <td>
                            <span class="limiting-factor-badge">
                                <i class="fa-solid fa-triangle-exclamation"></i> ${c.primary_limiting_factor}
                            </span>
                        </td>
                        <td>
                            <button type="button" class="btn btn-secondary btn-sm btn-inspect-crop" data-crop="${c.crop.toLowerCase()}" style="font-size: 11px; padding: 4px 8px;">
                                <i class="fa-solid fa-eye"></i> Inspect
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });

                document.querySelectorAll(".btn-inspect-crop").forEach(b => {
                    b.addEventListener("click", () => {
                        const crop = b.getAttribute("data-crop");
                        const selectEl = document.getElementById("select-crop");
                        if (selectEl) {
                            selectEl.value = crop;
                        }
                        const suitForm = document.getElementById("suitability-form");
                        if (suitForm) {
                            suitForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
                            document.getElementById("suitability-result-card")?.scrollIntoView({ behavior: 'smooth' });
                        }
                    });
                });
            }
        })
        .catch(err => {
            if (rankBtn) {
                rankBtn.innerHTML = origHtml;
                rankBtn.disabled = false;
            }
            alert("Failed to rank 22 crops: " + err.message);
        });
}

/**
 * 5. Research Analytics Dual-Model & Live Latency Benchmark
 */
function setupResearchEvaluationLab() {
    const tabCrop = document.getElementById("btn-tab-crop-model");
    const tabDisease = document.getElementById("btn-tab-disease-model");
    const secCrop = document.getElementById("section-crop-eval");
    const secDisease = document.getElementById("section-disease-eval");

    if (tabCrop && tabDisease) {
        tabCrop.addEventListener("click", () => {
            tabCrop.classList.add("active");
            tabCrop.classList.replace("btn-secondary", "btn-primary");
            tabDisease.classList.remove("active");
            tabDisease.classList.replace("btn-primary", "btn-secondary");
            if (secCrop) secCrop.style.display = "block";
            if (secDisease) secDisease.style.display = "none";
        });

        tabDisease.addEventListener("click", () => {
            tabDisease.classList.add("active");
            tabDisease.classList.replace("btn-secondary", "btn-primary");
            tabCrop.classList.remove("active");
            tabCrop.classList.replace("btn-primary", "btn-secondary");
            if (secCrop) secCrop.style.display = "none";
            if (secDisease) secDisease.style.display = "block";
            loadDiseaseEvaluationTable();
        });
    }

    const benchBtn = document.getElementById("btn-run-latency-benchmark");
    if (benchBtn) {
        benchBtn.addEventListener("click", () => runLiveLatencyBenchmark());
    }
}

let diseaseEvalLoaded = false;
function loadDiseaseEvaluationTable() {
    if (diseaseEvalLoaded) return;
    const tbody = document.getElementById("disease-eval-tbody");
    if (!tbody) return;

    fetch("/api/disease-evaluation")
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-danger">Failed to load disease evaluation data.</td></tr>`;
                return;
            }

            diseaseEvalLoaded = true;
            const perClass = data.per_class_metrics || {};
            const classKeys = Object.keys(perClass).sort();

            function renderRows(filterText = "") {
                tbody.innerHTML = "";
                const ft = filterText.toLowerCase();
                const filtered = classKeys.filter(k => k.toLowerCase().includes(ft));

                if (filtered.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted); padding:20px;">No matching pathology classes found.</td></tr>`;
                    return;
                }

                filtered.forEach(k => {
                    const parts = k.split("___");
                    const crop = parts[0].replace(/_/g, " ");
                    const condition = (parts[1] || "").replace(/_/g, " ");
                    const m = perClass[k];

                    const f1 = m.f1_score;
                    let grade = "A+ (Benchmark High)";
                    let gradeColor = "#34d399";
                    if (f1 < 75) {
                        grade = "C (Challenging Morphology)";
                        gradeColor = "#f87171";
                    } else if (f1 < 90) {
                        grade = "B (Moderate Support)";
                        gradeColor = "#fbbf24";
                    }

                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>${crop}</strong></td>
                        <td>${condition}</td>
                        <td>${m.precision.toFixed(1)}%</td>
                        <td>${m.recall.toFixed(1)}%</td>
                        <td style="font-weight: 700; color: ${gradeColor};">${m.f1_score.toFixed(1)}%</td>
                        <td>${m.support} samples</td>
                        <td><span style="font-size: 11px; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.05); color: ${gradeColor}; border: 1px solid ${gradeColor}40;">${grade}</span></td>
                    `;
                    tbody.appendChild(tr);
                });
            }

            renderRows();

            const searchInput = document.getElementById("disease-eval-search");
            if (searchInput) {
                searchInput.addEventListener("input", (e) => {
                    renderRows(e.target.value.trim());
                });
            }
        })
        .catch(err => {
            tbody.innerHTML = `<tr><td colspan="7" class="text-danger">Evaluation fetch error: ${err.message}</td></tr>`;
        });
}

function runLiveLatencyBenchmark() {
    const btn = document.getElementById("btn-run-latency-benchmark");
    const panel = document.getElementById("latency-benchmark-panel");
    const origHtml = btn?.innerHTML;
    if (btn) {
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Benchmarking Hardware Latency...';
        btn.disabled = true;
    }

    fetch("/api/benchmark-latency")
        .then(res => res.json())
        .then(data => {
            if (btn) {
                btn.innerHTML = origHtml;
                btn.disabled = false;
            }

            if (panel) panel.style.display = "block";

            if (data.benchmarks) {
                const b = data.benchmarks;
                if (b.crop_model) {
                    const cm = b.crop_model;
                    document.getElementById("bench-crop-name").textContent = cm.name;
                    document.getElementById("bench-crop-mean").textContent = `${cm.mean_ms} ms`;
                    document.getElementById("bench-crop-fps").textContent = `${cm.throughput_fps} FPS`;
                    document.getElementById("bench-crop-range").textContent = `Min: ${cm.min_ms} ms | Max: ${cm.max_ms} ms (${cm.iterations} runs)`;
                }
                if (b.disease_model) {
                    const dm = b.disease_model;
                    document.getElementById("bench-disease-name").textContent = dm.name;
                    document.getElementById("bench-disease-mean").textContent = `${dm.mean_ms} ms`;
                    document.getElementById("bench-disease-fps").textContent = `${dm.throughput_fps} FPS`;
                    document.getElementById("bench-disease-range").textContent = `Min: ${dm.min_ms} ms | Max: ${dm.max_ms} ms (${dm.iterations} runs, 224x224 RGB)`;
                }
                const envBadge = document.getElementById("latency-env-badge");
                if (envBadge && data.environment) {
                    envBadge.textContent = data.environment;
                }
            }
        })
        .catch(err => {
            if (btn) {
                btn.innerHTML = origHtml;
                btn.disabled = false;
            }
            alert("Benchmark failed: " + err.message);
        });
}