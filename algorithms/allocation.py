"""
Allocation of Frames (Unit 3: Virtual Memory).

Implements the classic allocation schemes from the syllabus and compares
local vs global page replacement:
  * Equal allocation        : every process gets m / n frames
  * Proportional allocation : a_i = (s_i / S) * m, where s_i is the process size
  * Local replacement       : each process replaces only inside its own frames
  * Global replacement      : all processes compete for one shared pool of frames
"""


def _validate(total_frames, n_procs):
    if n_procs < 1:
        raise ValueError("At least one process is required.")
    if total_frames < n_procs:
        raise ValueError(
            f"Total frames ({total_frames}) must be at least the number of processes ({n_procs}); "
            "every process needs a minimum of one frame."
        )


def equal_allocation(total_frames, n_procs):
    """Split frames as evenly as possible; leftover frames go to the first processes."""
    _validate(total_frames, n_procs)
    base, extra = divmod(total_frames, n_procs)
    return [base + (1 if i < extra else 0) for i in range(n_procs)]


def proportional_allocation(total_frames, sizes):
    """
    a_i = s_i / S * m, rounded down, minimum 1 frame per process.
    Leftover frames go to the largest fractional remainders so the total equals m.
    """
    _validate(total_frames, len(sizes))
    if any(s <= 0 for s in sizes):
        raise ValueError("Process sizes must be positive.")

    n = len(sizes)
    total_size = sum(sizes)
    raw = [s / total_size * total_frames for s in sizes]
    alloc = [max(1, int(r)) for r in raw]

    while sum(alloc) < total_frames:
        i = max(range(n), key=lambda k: raw[k] - alloc[k])
        alloc[i] += 1
    while sum(alloc) > total_frames:
        candidates = [k for k in range(n) if alloc[k] > 1]
        i = max(candidates, key=lambda k: alloc[k] - raw[k])
        alloc[i] -= 1
    return alloc


def interleave(proc_refs):
    """Round-robin interleave of per-process reference strings -> list of (pid, page)."""
    idx = [0] * len(proc_refs)
    merged = []
    while any(idx[p] < len(proc_refs[p]) for p in range(len(proc_refs))):
        for p, refs in enumerate(proc_refs):
            if idx[p] < len(refs):
                merged.append((p, refs[idx[p]]))
                idx[p] += 1
    return merged


def simulate_local(proc_refs, allocation, algo_fn):
    """Local replacement: each process runs the algorithm on its own fixed allocation."""
    rows = []
    for p, (refs, frames) in enumerate(zip(proc_refs, allocation)):
        _, hits, faults = algo_fn(refs, frames)
        rows.append({"process": p, "frames": frames, "hits": hits, "faults": faults, "refs": len(refs)})
    return rows


def simulate_global(proc_refs, total_frames, algo_fn):
    """
    Global replacement: one shared pool. Pages are tagged (pid, page) so identical page
    numbers in different processes stay distinct. Any process may lose a frame to another.
    """
    _validate(total_frames, len(proc_refs))
    merged = interleave(proc_refs)
    results, _, _ = algo_fn(merged, total_frames)

    rows = []
    final_frames = results[-1]["PhysicalFrames"] if results else []
    for p, refs in enumerate(proc_refs):
        faults = sum(1 for r in results if r["Page"][0] == p and r["Status"] == "Fault")
        held = sum(1 for f in final_frames if f is not None and f[0] == p)
        rows.append({"process": p, "frames": held, "hits": len(refs) - faults, "faults": faults, "refs": len(refs)})
    return rows
