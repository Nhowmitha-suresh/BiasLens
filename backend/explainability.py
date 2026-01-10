import numpy as np

def explain_bias(data):
    sensitive = np.array(data["sensitive"])
    correlations = {}

    for feature, values in data["features"].items():
        values = np.array(values)
        if len(values) != len(sensitive):
            continue
        corr = np.corrcoef(values, sensitive)[0, 1]
        correlations[feature] = round(float(corr), 3)

    driver = max(correlations, key=lambda x: abs(correlations[x]))

    return {
        "feature_correlations": correlations,
        "main_bias_driver": driver,
        "explanation": f"'{driver}' is strongly correlated with the sensitive attribute."
    }
