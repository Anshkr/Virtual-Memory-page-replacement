"""
Demand Segmentation (Unit 3: Virtual Memory).

Segments are variable-sized logical units loaded only when referenced. To fit a new
segment, resident segments are evicted (LRU or FIFO) until enough memory is free.
Simplification: memory is assumed compacted, so external fragmentation is not modelled.
"""


def demand_segmentation(reference_string, segment_sizes, capacity, policy="LRU"):
    """Returns (results, hits, faults), like the paging algorithms."""
    if policy not in ("LRU", "FIFO"):
        raise ValueError("Policy must be 'LRU' or 'FIFO'.")
    if capacity <= 0:
        raise ValueError("Memory capacity must be positive.")
    for seg in reference_string:
        if seg not in segment_sizes:
            raise ValueError(f"Segment {seg} is referenced but not defined in the segment table.")
        if segment_sizes[seg] <= 0:
            raise ValueError(f"Segment {seg} must have a positive size.")
        if segment_sizes[seg] > capacity:
            raise ValueError(
                f"Segment {seg} ({segment_sizes[seg]} KB) is larger than memory ({capacity} KB) and can never be loaded."
            )

    resident = []  # eviction order: first element is the next victim
    used = 0
    hits = faults = 0
    results = []

    for seg in reference_string:
        evicted = []
        if seg in resident:
            status = "Hit"
            hits += 1
            if policy == "LRU":
                resident.remove(seg)
                resident.append(seg)
            reason = f"Segment {seg} already resident."
        else:
            status = "Fault"
            faults += 1
            size = segment_sizes[seg]
            while used + size > capacity:
                victim = resident.pop(0)
                used -= segment_sizes[victim]
                evicted.append(victim)
            resident.append(seg)
            used += size
            reason = f"Segment {seg} ({size} KB) loaded on demand."
            if evicted:
                reason += f" Evicted {evicted} ({policy}) to make room."

        results.append({
            "Segment": seg,
            "Resident": list(resident),
            "Used": used,
            "Free": capacity - used,
            "Status": status,
            "Evicted": evicted,
            "Reason": reason,
        })
    return results, hits, faults
