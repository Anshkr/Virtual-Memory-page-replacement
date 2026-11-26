"""
Thrashing and the Working-Set Model (Unit 3: Virtual Memory).

Thrashing: a process spends more time paging than executing because it is given fewer
frames than its working set needs. Here it is detected from the fault ratio produced
by any page-replacement algorithm in this project.
"""


def working_set_sizes(reference_string, delta):
    """WSS(t): number of distinct pages among the last `delta` references ending at step t."""
    if delta < 1:
        raise ValueError("Working-set window must be at least 1.")
    return [
        len(set(reference_string[max(0, t - delta + 1): t + 1]))
        for t in range(len(reference_string))
    ]


def slowdown_factor(fault_ratio, mat_ns, pfst_ns):
    """How many times slower than a fault-free run: EMAT / MAT."""
    emat = (1.0 - fault_ratio) * mat_ns + fault_ratio * pfst_ns
    return emat / mat_ns


def analyze_thrashing(reference_string, algo_fn, max_frames, mat_ns, pfst_ns, threshold=0.5):
    """Sweep frame counts 1..max_frames; flag fault ratio >= threshold caused by more than compulsory misses."""
    n = len(reference_string)
    if n == 0:
        raise ValueError("Reference string cannot be empty.")
    distinct = len(set(reference_string))  # first-touch (compulsory) misses are unavoidable
    rows = []
    for frames in range(1, max_frames + 1):
        _, hits, faults = algo_fn(reference_string, frames)
        ratio = faults / n
        rows.append({
            "Frames": frames,
            "Faults": faults,
            "Fault Ratio": ratio,
            "Slowdown (x)": slowdown_factor(ratio, mat_ns, pfst_ns),
            "Thrashing": ratio >= threshold and faults > distinct,
        })
    return rows


def recommended_frames(rows):
    """Smallest frame count that is not thrashing, or None if every count thrashes."""
    for r in rows:
        if not r["Thrashing"]:
            return r["Frames"]
    return None
