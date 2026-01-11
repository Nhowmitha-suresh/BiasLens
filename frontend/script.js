const ANALYZE_URL = "http://127.0.0.1:5000/analyze";
const REPORT_URL = "http://127.0.0.1:5000/report";

const analyzeBtn = document.getElementById("analyzeBtn");
const downloadBtn = document.getElementById("downloadBtn");
const statusDiv = document.getElementById("status");
const resultsDiv = document.getElementById("results");
const explanationDiv = document.getElementById("explanation");
const table = document.getElementById("previewTable");

let chart = null;
let lastResult = null;

function setStatus(msg, color) {
    statusDiv.innerText = msg;
    statusDiv.style.color = color;
}

analyzeBtn.onclick = async () => {
    const file = document.getElementById("dataset").files[0];
    const sensitive = document.getElementById("sensitive").value.trim();

    if (!file || !sensitive) {
        setStatus("❌ Upload CSV and enter sensitive attribute", "red");
        return;
    }

    const fd = new FormData();
    fd.append("dataset", file);
    fd.append("sensitive", sensitive);

    setStatus("⏳ Analyzing bias...", "#ffcc00");

    try {
        const res = await fetch(ANALYZE_URL, {
            method: "POST",
            body: fd
        });

        const data = await res.json();

        if (data.error) throw new Error(data.error);

        lastResult = data; // 🔥 REQUIRED FOR SIDE FUNCTIONS

        renderResults(data);
        renderTable(data);

        setStatus("✅ Analysis complete", "#4caf50");

    } catch (err) {
        console.error(err);
        setStatus("❌ " + err.message, "red");
    }
};

downloadBtn.onclick = async () => {
    if (!lastResult) {
        alert("Run bias analysis first!");
        return;
    }

    const res = await fetch(REPORT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(lastResult)
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "BiasLens_Report.pdf";
    a.click();
};

function renderResults(data) {
    resultsDiv.innerHTML = `
        <p><b>Rows:</b> ${data.rows}</p>
        <p><b>Sensitive Attribute:</b> ${data.sensitive_attribute}</p>
        <p><b>Type:</b> ${data.attribute_type}</p>
        <p><b>Disparate Impact:</b> ${data.disparate_impact}</p>
        <p><b>Statistical Parity Difference:</b> ${data.statistical_parity_difference}</p>
    `;

    explanationDiv.innerText = data.explanation;

    const labels = Object.keys(data.group_distribution);
    const values = Object.values(data.group_distribution).map(v => v * 100);

    const ctx = document.getElementById("biasChart").getContext("2d");

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Group Distribution (%)",
                data: values,
                backgroundColor: "#ffcc00"
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function renderTable(data) {
    table.innerHTML = "";

    const header = table.insertRow();
    data.columns?.forEach(col => {
        const th = document.createElement("th");
        th.innerText = col;
        if (col === data.sensitive_attribute) th.classList.add("highlight");
        header.appendChild(th);
    });

    (data.preview || []).forEach(row => {
        const tr = table.insertRow();
        data.columns.forEach(col => {
            const td = tr.insertCell();
            td.innerText = row[col];
            if (col === data.sensitive_attribute) td.classList.add("highlight");
        });
    });
}
