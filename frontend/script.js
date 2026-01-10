/* =====================================================
   BiasLens – Frontend Script (FULLY FIXED)
   ===================================================== */

   document.addEventListener("DOMContentLoaded", function () {
    console.log("script.js loaded successfully");

    const analyzeBtn = document.getElementById("analyzeBtn");

    if (!analyzeBtn) {
        console.error("Analyze button not found");
        return;
    }

    analyzeBtn.addEventListener("click", analyzeDataset);
});

/* =====================================================
   Main function
   ===================================================== */
function analyzeDataset() {
    const fileInput = document.getElementById("file");
    const sensitiveInput = document.getElementById("sensitive");
    const resultDiv = document.getElementById("result");

    console.log("Analyze button clicked");

    // Validation
    if (!fileInput.files.length) {
        alert("Please upload a dataset file");
        return;
    }

    if (!sensitiveInput.value.trim()) {
        alert("Please enter a sensitive attribute (e.g. gender)");
        return;
    }

    // Loading UI
    resultDiv.innerHTML = `
        <p class="placeholder">Analyzing dataset… ⏳</p>
    `;

    // Prepare data
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("sensitive", sensitiveInput.value.trim());

    // Call backend
    fetch("http://127.0.0.1:5000/dataset-bias", {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Backend error");
        }
        return response.json();
    })
    .then(data => {
        renderResult(data);
    })
    .catch(error => {
        console.error(error);
        resultDiv.innerHTML = `
            <p style="color:#c0392b; text-align:center;">
                Backend not reachable. Make sure Flask server is running.
            </p>
        `;
    });
}

/* =====================================================
   Render Result
   ===================================================== */
function renderResult(data) {
    const resultDiv = document.getElementById("result");

    const riskScore = data.bias_detected ? 80 : 20;
    const riskClass = data.bias_detected ? "high" : "low";
    const riskText = data.bias_detected ? "High Bias Risk" : "Low Bias Risk";

    let distributionHTML = "";
    for (let key in data.distribution) {
        distributionHTML += `
            <li>${key}: ${data.distribution[key].toFixed(2)}%</li>
        `;
    }

    resultDiv.innerHTML = `
        <h2>Analysis Result</h2>

        <p><strong>Status:</strong> ${data.message}</p>

        <p class="bias-risk ${riskClass}">
            ${riskText} (${riskScore}/100)
        </p>

        <div class="progress-bar">
            <div class="progress-fill" style="width:${riskScore}%;"></div>
        </div>

        <h3 style="margin-top:16px;">Group Distribution</h3>
        <ul style="margin-left:18px;">
            ${distributionHTML}
        </ul>
    `;
}
