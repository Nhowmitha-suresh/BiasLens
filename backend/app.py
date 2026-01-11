from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import datetime
import tempfile
import os

app = Flask(__name__)
CORS(app)

def generate_explanation(di, spd, sensitive):
    if di < 0.6 or spd > 0.2:
        return f"High bias detected for '{sensitive}'. One group is significantly disadvantaged."
    elif di < 0.8 or spd > 0.1:
        return f"Potential bias detected for '{sensitive}'. Distribution is imbalanced."
    else:
        return f"No significant bias detected for '{sensitive}'. Groups are fairly represented."

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

        if pd.api.types.is_numeric_dtype(col):
            df["_group_"] = pd.cut(col, bins=[0,30,45,100], labels=["18–30","31–45","46+"])
            group_col = "_group_"
            attr_type = "numeric (bucketed)"
        else:
            group_col = sensitive
            attr_type = "categorical"

        dist = df[group_col].value_counts(normalize=True).to_dict()
        min_r, max_r = min(dist.values()), max(dist.values())

        di = round(min_r / max_r, 3)
        spd = round(max_r - min_r, 3)

        explanation = generate_explanation(di, spd, sensitive)

        return jsonify({
            "status": "success",
            "rows": len(df),
            "sensitive_attribute": sensitive,
            "attribute_type": attr_type,
            "group_distribution": dist,
            "disparate_impact": di,
            "statistical_parity_difference": spd,
            "explanation": explanation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/report", methods=["POST"])
def generate_report():
    data = request.json

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp.name, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, y, "BiasLens – Bias Analysis Report")

    y -= 40
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Generated on: {datetime.datetime.now()}")

    y -= 30
    c.drawString(50, y, f"Sensitive Attribute: {data['sensitive_attribute']}")
    y -= 20
    c.drawString(50, y, f"Attribute Type: {data['attribute_type']}")
    y -= 20
    c.drawString(50, y, f"Total Records: {data['rows']}")

    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Fairness Metrics")

    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Disparate Impact (DI): {data['disparate_impact']}")
    y -= 20
    c.drawString(50, y, f"Statistical Parity Difference (SPD): {data['statistical_parity_difference']}")

    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Bias Explanation")

    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(50, y, data["explanation"])

    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Group Distribution")

    y -= 20
    c.setFont("Helvetica", 12)
    for k, v in data["group_distribution"].items():
        c.drawString(60, y, f"{k}: {round(v*100,2)}%")
        y -= 18

    c.showPage()
    c.save()

    return send_file(temp.name, as_attachment=True, download_name="BiasLens_Report.pdf")


if __name__ == "__main__":
    print("🚀 BiasLens running on http://127.0.0.1:5000")
    app.run(debug=True)
