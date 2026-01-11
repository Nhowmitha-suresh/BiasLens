from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)   # 🔥 REQUIRED

@app.route("/analyze", methods=["POST"])
def analyze_bias():
    try:
        # Check file
        if "dataset" not in request.files:
            return jsonify({"error": "Dataset file missing"}), 400

        file = request.files["dataset"]
        sensitive = request.form.get("sensitive")

        if not sensitive:
            return jsonify({"error": "Sensitive attribute missing"}), 400

        # Read CSV
        df = pd.read_csv(file)

        if sensitive not in df.columns:
            return jsonify({
                "error": f"Column '{sensitive}' not found in dataset"
            }), 400

        # Simple bias stats
        counts = df[sensitive].value_counts(normalize=True).to_dict()

        return jsonify({
            "status": "success",
            "sensitive_attribute": sensitive,
            "rows": len(df),
            "bias_metrics": counts,
            "disparate_impact": round(min(counts.values()) / max(counts.values()), 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 BiasLens server starting on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
