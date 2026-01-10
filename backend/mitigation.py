def mitigation_suggestions(data):
    recs = []

    if data.get("dataset_bias"):
        recs.append("Rebalance the dataset.")

    if data.get("accuracy_gap", 0) > 0.1:
        recs.append("Adjust thresholds or retrain with fairness constraints.")

    if data.get("proxy_feature"):
        recs.append(f"Remove proxy feature: {data['proxy_feature']}")

    if not recs:
        recs.append("No major bias detected.")

    return {"recommendations": recs}
