def lru(reference_string, frame_count):
    """
    Least Recently Used (LRU) Page Replacement Algorithm.
    Maintains fixed physical memory frame slots and evicts the page with the oldest access time.
    """
    physical_frames = [None] * frame_count
    last_access_time = {}  # page -> step index
    page_faults = 0
    page_hits = 0
    results = []

    for t, page in enumerate(reference_string):
        evicted = None
        victim_slot = None
        reason = ""

        # Check if page is already in memory
        if page in physical_frames:
            status = "Hit"
            page_hits += 1
            victim_slot = physical_frames.index(page)
            last_access_time[page] = t
            reason = f"Page {page} found in Frame {victim_slot + 1}. Last access updated to Step {t + 1}."
        else:
            status = "Fault"
            page_faults += 1

            # Check for an empty slot first
            if None in physical_frames:
                victim_slot = physical_frames.index(None)
                physical_frames[victim_slot] = page
                last_access_time[page] = t
                reason = f"Page {page} allocated to empty Frame {victim_slot + 1}."
            else:
                # Find page in physical frames with smallest last_access_time
                victim_page = min(physical_frames, key=lambda p: last_access_time.get(p, -1))
                victim_slot = physical_frames.index(victim_page)
                evicted = victim_page
                reason = (
                    f"Page {victim_page} in Frame {victim_slot + 1} was least recently used "
                    f"(last at Step {last_access_time[victim_page] + 1}); replaced by Page {page}."
                )
                physical_frames[victim_slot] = page
                last_access_time[page] = t

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
