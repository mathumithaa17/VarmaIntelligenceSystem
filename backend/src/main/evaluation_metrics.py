import numpy as np
import pandas as pd
from typing import Dict, List
from .lexical_matching import _normalize_text

def calculate_metrics_with_ground_truth(
    predictions_df: pd.DataFrame,
    ground_truth_dict: Dict,
    query_times: List[float]
) -> Dict[str, float]:
    
    total = 0
    top5_correct = 0
    average_precisions = []

    for _, row in predictions_df.iterrows():
        test_id = str(row["test_id"])
        predicted_str = str(row["predicted"]) if pd.notna(row["predicted"]) else ""

        if test_id not in ground_truth_dict:
            continue

        ground_truth = ground_truth_dict[test_id]
        if not ground_truth:
            continue

        total += 1
        predicted = [p.strip() for p in predicted_str.split(";") if p.strip()]

        gt_norm = [_normalize_text(x) for x in ground_truth]
        pred_norm = [_normalize_text(x) for x in predicted]

        if any(gt in pred_norm[:5] for gt in gt_norm):
            top5_correct += 1

        gt_set = set(gt_norm)
        relevant_found = 0
        precisions = []

        for i, pred in enumerate(pred_norm, start=1):
            if pred in gt_set:
                relevant_found += 1
                precisions.append(relevant_found / i)

        average_precisions.append(np.mean(precisions) if precisions else 0.0)

    if total == 0:
        print("WARNING: No valid test cases found!")
        return {}

    avg_query_time = float(np.mean(query_times)) if query_times else 0.0

    metrics = {
        "total_test_cases": total,
        "accuracy_top_5": (top5_correct / total) * 100,
        "mean_average_precision": float(np.mean(average_precisions)),
        "avg_query_processing_time_sec": avg_query_time
    }

    return metrics

def print_metrics_report(metrics: Dict[str, float]):
    if not metrics:
        print("No metrics available.")
        return

    print("\n" + "=" * 70)
    print("PERFORMANCE METRICS REPORT (TOP-5)")
    print("=" * 70)

    print(f"Total Test Cases           : {metrics['total_test_cases']}")
    print(f"Accuracy (Top-5)           : {metrics['accuracy_top_5']:.2f}%")
    print(f"Mean Average Precision     : {metrics['mean_average_precision']:.4f}")
    print(f"Avg Query Time (seconds)   : {metrics['avg_query_processing_time_sec']:.4f}")

    print("=" * 70)