def fifo(reference_string, frame_count):
    """
    First-In, First-Out (FIFO) Page Replacement Algorithm.
    Maintains fixed physical memory frame slots and tracks arrival order.
    """
    physical_frames = [None] * frame_count
    load_order = []  # stores slot indices in order of page loading
    page_faults = 0
    page_hits = 0
    results = []

    for page in reference_string:
        evicted = None
        victim_slot = None
        reason = ""

        # Check whether page is already in physical memory
        if page in physical_frames:
            status = "Hit"
            page_hits += 1
            victim_slot = physical_frames.index(page)
            reason = f"Page {page} found in Frame {victim_slot + 1}."
        else:
            status = "Fault"
            page_faults += 1

            # Check for an empty slot first
            if None in physical_frames:
                victim_slot = physical_frames.index(None)
                physical_frames[victim_slot] = page
                load_order.append(victim_slot)
                reason = f"Page {page} allocated to empty Frame {victim_slot + 1}."
            else:
                # Evict oldest loaded frame
                victim_slot = load_order.pop(0)
                evicted = physical_frames[victim_slot]
                reason = f"Page {evicted} in Frame {victim_slot + 1} was oldest; replaced by Page {page}."
                physical_frames[victim_slot] = page
                load_order.append(victim_slot)

        active_frames = [p for p in physical_frames if p is not None]

        results.append({
            "Page": page,
            "Frames": active_frames,
            "PhysicalFrames": list(physical_frames),
            "Status": status,
            "Evicted": evicted,
            "VictimSlot": victim_slot,
            "Reason": reason
        })

    return results, page_hits, page_faults
