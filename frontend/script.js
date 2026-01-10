function analyzeDataset() {
    const fileInput = document.getElementById("file");
    const sensitive = document.getElementById("sensitive").value;
    const resultDiv = document.getElementById("result");

    if (!fileInput.files.length || !sensitive) {
        alert("Please upload dataset and enter sensitive attribute");
        return;
    }

    resultDiv.innerHTML = "<p>Analyzing… ⏳</p>";

    let formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("sensitive", sensitive);

    fetch("http://127.0.0.1:5000/dataset-bias", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        const risk = data.bias_detected ? 80 : 20;
        const color = risk > 50 ? "#ef4444" : "#22c55e";

        resultDiv.innerHTML = `
            <h2>Result</h2>
            <p><b>Status:</b> ${data.message}</p>
            <p><b>Bias Risk:</b> 
                <span style="color:${color}; font-weight:bold;">
                    ${risk}/100
                </span>
            </p>
            <pre>${JSON.stringify(data.distribution, null, 2)}</pre>
        `;
    })
    .catch(() => {
        resultDiv.innerHTML = "<p style='color:red'>Backend not reachable</p>";
    });
}
