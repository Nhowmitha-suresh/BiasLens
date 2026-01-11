const BACKEND_URL = "http://127.0.0.1:5000/analyze";
const REPORT_URL = "http://127.0.0.1:5000/report";

const analyzeBtn = document.getElementById("analyzeBtn");
const downloadBtn = document.getElementById("downloadBtn");
const statusDiv = document.getElementById("status");

let lastResult = null;

analyzeBtn.onclick = async () => {
    const file = document.getElementById("dataset").files[0];
    const sensitive = document.getElementById("sensitive").value.trim();

    if (!file || !sensitive) {
        statusDiv.innerText = "❌ Upload CSV and enter sensitive attribute";
        return;
    }

    const fd = new FormData();
    fd.append("dataset", file);
    fd.append("sensitive", sensitive);

    statusDiv.innerText = "⏳ Analyzing...";

    const res = await fetch(BACKEND_URL, { method: "POST", body: fd });
    const data = await res.json();

    if (data.error) {
        statusDiv.innerText = "❌ " + data.error;
        return;
    }

    lastResult = data;
    statusDiv.innerText = "✅ Analysis complete";
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
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "BiasLens_Report.pdf";
    a.click();
};
