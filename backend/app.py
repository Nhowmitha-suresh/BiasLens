from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import requests
import tempfile
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# -------------------------------
# App setup
# -------------------------------
app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"   # fast + reliable (recommended)

# -------------------------------
# Ollama explanation (SAFE)
# -------------------------------
def ollama_explanation(di, spd, sensitive, dist):
    prompt = f"""
You are an ethical AI auditor.

Explain the bias analysis results in simple, non-technical language.

Sensitive attribute: {sensitive}
Group distribution: {dist}
Disparate Impact (DI): {di}
Statistical Parity Difference (SPD): {spd}

Explain:
1. Whether bias exists
2. Why it matters
3. What can be improved
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=90   # ⏳ increased timeout
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()

    except requests.exceptions.Timeout:
        return (
            "LLM explanation timed out. "
            "However, the fairness metrics indicate potential bias. "
            "Please review Disparate Impact and Statistical Parity Difference."
        )

    except Exception:
        return (
            "LLM explanation could not be generated. "
            "Please review the fairness metrics manually."
        )

# -------------------------------
# Bias analysis API
# -------------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files.get("dataset")
        sensitive = request.form.get("sensitive")

        if not file or not sensitive:
            return jsonify({"error": "Missing dataset or sensitive attribute"}), 400

        df = pd.read_csv(file)

        if sensitive not in df.columns:
            return jsonify({"error": f"Column '{sensitive}' not found"}), 400

        col = df[sensitive]

        # Auto-detect type
        if pd.api.types.is_numeric_dtype(col):
            df["_group_"] = pd.cut(
                col,
                bins=[0, 30, 45, 100],
                labels=["18–30", "31–45", "46+"]
            )
            group_col = "_group_"
            attr_type = "numeric (bucketed)"
        else:
            group_col = sensitive
            attr_type = "categorical"

        dist = df[group_col].value_counts(normalize=True).to_dict()
        min_r, max_r = min(dist.values()), max(dist.values())

        di = round(min_r / max_r, 3)
        spd = round(max_r - min_r, 3)

        explanation = ollama_explanation(di, spd, sensitive, dist)

        return jsonify({
            "status": "success",
            "rows": len(df),
            "sensitive_attribute": sensitive,
            "attribute_type": attr_type,
            "group_distribution": dist,
            "disparate_impact": di,
            "statistical_parity_difference": spd,
            "explanation": explanation,
            "explanation_type": "ollama (local)"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# PDF Report API
# -------------------------------
@app.route("/report", methods=["POST"])
def report():
    data = request.json

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp.name, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, y, "BiasLens – Bias Analysis Report")

    y -= 30
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Generated on: {datetime.datetime.now()}")

    y -= 25
    c.drawString(50, y, f"Sensitive Attribute: {data['sensitive_attribute']}")
    y -= 18
    c.drawString(50, y, f"Attribute Type: {data['attribute_type']}")
    y -= 18
    c.drawString(50, y, f"Total Records: {data['rows']}")

    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Fairness Metrics")

    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Disparate Impact (DI): {data['disparate_impact']}")
    y -= 18
    c.drawString(50, y, f"Statistical Parity Difference (SPD): {data['statistical_parity_difference']}")

    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Bias Explanation")

    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(50, y, data["explanation"])

    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Group Distribution")

    y -= 18
    c.setFont("Helvetica", 11)
    for k, v in data["group_distribution"].items():
        c.drawString(60, y, f"{k}: {round(v * 100, 2)}%")
        y -= 15

    c.showPage()
    c.save()

    return send_file(
        temp.name,
        as_attachment=True,
        download_name="BiasLens_Report.pdf"
    )

# -------------------------------
# Run app
# -------------------------------
if __name__ == "__main__":
    print("🚀 BiasLens backend running with Ollama (local LLM)")
    app.run(debug=True)
