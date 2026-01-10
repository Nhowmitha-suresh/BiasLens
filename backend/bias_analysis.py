def analyze_dataset_bias(df, sensitive_col):
    distribution = df[sensitive_col].value_counts(normalize=True) * 100
    bias_detected = any(distribution > 70)

    return {
        "distribution": distribution.to_dict(),
        "bias_detected": bias_detected,
        "message": "Bias detected" if bias_detected else "Dataset balanced"
    }
