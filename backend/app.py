from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

from bias_analysis import analyze_dataset_bias
from model_evaluation import evaluate_model_bias
from explainability import explain_bias
from mitigation import mitigation_suggestions

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return {"status": "BiasLens backend running"}

@app.route("/dataset-bias", methods=["POST"])
def dataset_bias():
    file = request.files["file"]
    sensitive = request.form["sensitive"]
    df = pd.read_csv(file)
    return jsonify(analyze_dataset_bias(df, sensitive))

if __name__ == "__main__":
    print("🚀 BiasLens server starting on http://127.0.0.1:5000")
    app.run(debug=True)
