def summarize_metrics(adaptive, fixed):
    adaptive_avg = adaptive["total_wait"] / max(adaptive["wait_samples"], 1)
    fixed_avg = fixed["total_wait"] / max(fixed["wait_samples"], 1)
    # Positive means the adaptive controller has a lower average waiting score.
    improvement = ((fixed_avg - adaptive_avg) / fixed_avg * 100) if fixed_avg else 0.0
    return {
        "adaptive_avg_wait": adaptive_avg,
        "fixed_avg_wait": fixed_avg,
        "wait_improvement_pct": improvement,
    }
