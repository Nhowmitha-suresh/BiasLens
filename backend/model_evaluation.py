from sklearn.metrics import accuracy_score

def evaluate_model_bias(y_true, y_pred, groups):
    results = {}

    for g in set(groups):
        idx = [i for i, v in enumerate(groups) if v == g]
        acc = accuracy_score(
            [y_true[i] for i in idx],
            [y_pred[i] for i in idx]
        )
        results[g] = round(acc, 3)

    gap = max(results.values()) - min(results.values())

    return {
        "group_accuracy": results,
        "accuracy_gap": round(gap, 3),
        "bias_detected": gap > 0.1
    }
