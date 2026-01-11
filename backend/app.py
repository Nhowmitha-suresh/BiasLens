from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze_bias():
    try:
        if "dataset" not in request.files:
            return jsonify({"error": "Dataset file missing"}), 400

        file = request.files["dataset"]
        sensitive = request.form.get("sensitive")

        if not sensitive:
            return jsonify({"error": "Sensitive attribute missing"}), 400

        df = pd.read_csv(file)

        if sensitive not in df.columns:
            return jsonify({"error": f"Column '{sensitive}' not found"}), 400

        column = df[sensitive]

        # 🔹 AUTO-DETECT TYPE
        if pd.api.types.is_numeric_dtype(column):
            # Bucket numeric attribute
            bins = [0, 30, 45, 100]
            labels = ["18–30", "31–45", "46+"]
            df["__group__"] = pd.cut(column, bins=bins, labels=labels)
            group_col = "__group__"
            attribute_type = "numeric (bucketed)"
        else:
            group_col = sensitive
            attribute_type = "categorical"

        # 🔹 GROUP DISTRIBUTION
        group_rates = df[group_col].value_counts(normalize=True).to_dict()

        min_rate = min(group_rates.values())
        max_rate = max(group_rates.values())

        # 🔹 FAIRNESS METRICS
        disparate_impact = round(min_rate / max_rate, 3)
        statistical_parity_diff = round(max_rate - min_rate, 3)

        return jsonify({
            "status": "success",
            "sensitive_attribute": sensitive,
            "attribute_type": attribute_type,
            "rows": len(df),
            "group_distribution": group_rates,
            "disparate_impact": disparate_impact,
            "statistical_parity_difference": statistical_parity_diff
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 BiasLens server running on http://127.0.0.1:5000")
    app.run(debug=True)
