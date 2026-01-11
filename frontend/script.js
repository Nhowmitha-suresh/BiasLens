// ============================
// BiasLens Frontend Script
// ============================

// BACKEND URL (DO NOT CHANGE)
const BACKEND_URL = "http://127.0.0.1:5000/analyze";

// DOM
const analyzeBtn = document.getElementById("analyzeBtn");
const fileInput = document.getElementById("dataset");
const sensitiveInput = document.getElementById("sensitive");
const statusDiv = document.getElementById("status");
const resultsDiv = document.getElementById("results");

function setStatus(msg, color) {
    statusDiv.innerText = msg;
    statusDiv.style.color = color;
}

analyzeBtn.addEventListener("click", async () => {
    console.log("Analyze clicked");

    resultsDiv.innerHTML = "";

    if (!fileInput.files.length) {
        setStatus("❌ Upload a CSV file", "red");
        return;
    }

    if (!sensitiveInput.value.trim()) {
        setStatus("❌ Enter sensitive attribute", "red");
        return;
    }

    const formData = new FormData();
    formData.append("dataset", fileInput.files[0]);
    formData.append("sensitive", sensitiveInput.value.trim());

    setStatus("⏳ Sending data to backend...", "blue");

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
        console.log("Response:", data);

        setStatus("✅ Analysis complete", "green");

        let html = `<h4>Results</h4>`;
        html += `<p><b>Sensitive:</b> ${data.sensitive_attribute}</p>`;
        html += `<p><b>Rows:</b> ${data.rows}</p>`;

        if (data.bias_metrics) {
            html += "<ul>";
            for (let k in data.bias_metrics) {
                html += `<li>${k}: ${(data.bias_metrics[k] * 100).toFixed(2)}%</li>`;
            }
            html += "</ul>";
        }

        html += `<p><b>Disparate Impact:</b> ${data.disparate_impact}</p>`;

        resultsDiv.innerHTML = html;

    } catch (err) {
        console.error(err);
        setStatus("❌ Backend not reachable (port 5000)", "red");
    }
});
