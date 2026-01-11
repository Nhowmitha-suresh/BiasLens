// ============================
// BiasLens Phase 2 Script
// ============================

const BACKEND_URL = "http://127.0.0.1:5000/analyze";

const analyzeBtn = document.getElementById("analyzeBtn");
const fileInput = document.getElementById("dataset");
const sensitiveInput = document.getElementById("sensitive");
const statusDiv = document.getElementById("status");
const resultsDiv = document.getElementById("results");

let chart = null;

function setStatus(msg, color) {
    statusDiv.innerText = msg;
    statusDiv.style.color = color;
}

analyzeBtn.addEventListener("click", async () => {
    console.log("Analyze clicked");

    resultsDiv.innerHTML = "";
    setStatus("", "black");

    if (!fileInput.files.length) {
        setStatus("❌ Please upload a CSV file", "red");
        return;
    }

    if (!sensitiveInput.value.trim()) {
        setStatus("❌ Enter a sensitive attribute", "red");
        return;
    }

    const formData = new FormData();
    formData.append("dataset", fileInput.files[0]);
    formData.append("sensitive", sensitiveInput.value.trim());

    setStatus("⏳ Analyzing bias...", "blue");

    try {
        const response = await fetch(BACKEND_URL, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const txt = await response.text();
            throw new Error(txt);
        }

        const data = await response.json();
        console.log("Backend response:", data);

        setStatus("✅ Analysis completed", "green");
        displayResults(data);

    } catch (err) {
        console.error(err);
        setStatus("❌ Backend error (check Flask terminal)", "red");
    }
});

function displayResults(data) {
    const dist = data.group_distribution;

    // ---------- TEXT RESULTS ----------
    let html = `
        <h3>📊 Bias Analysis Results</h3>
        <p><b>Sensitive Attribute:</b> ${data.sensitive_attribute}</p>
        <p><b>Attribute Type:</b> ${data.attribute_type}</p>
        <p><b>Total Rows:</b> ${data.rows}</p>

        <h4>⚖️ Fairness Metrics</h4>
        <p><b>Disparate Impact:</b> ${data.disparate_impact}</p>
        <p><b>Statistical Parity Difference:</b> ${data.statistical_parity_difference}</p>
    `;

    // ---------- RISK INTERPRETATION ----------
    let riskText = "✅ Fair";
    let riskColor = "green";

    if (data.disparate_impact < 0.8 || data.statistical_parity_difference > 0.1) {
        riskText = "⚠️ Potential Bias Detected";
        riskColor = "orange";
    }

    if (data.disparate_impact < 0.6 || data.statistical_parity_difference > 0.2) {
        riskText = "🚨 High Bias Risk";
        riskColor = "red";
    }

    html += `<h4 style="color:${riskColor}">Bias Risk: ${riskText}</h4>`;
    resultsDiv.innerHTML = html;

    // ---------- BAR CHART ----------
    const labels = Object.keys(dist);
    const values = Object.values(dist).map(v => (v * 100).toFixed(2));

    const ctx = document.getElementById("biasChart").getContext("2d");

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Group Distribution (%)",
                data: values,
                backgroundColor: "#ffc107"
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Percentage"
                    }
                }
            }
        }
    });
}
