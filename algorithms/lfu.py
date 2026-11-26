def lfu(reference_string, frame_count):
    """
    Least Frequently Used (LFU) Page Replacement Algorithm.
    Evicts the page with the lowest access frequency.
    Ties are broken using FIFO (the page that has been in memory longest).
    """
    physical_frames = [None] * frame_count
    frequencies = {}      # page -> access count
    arrival_time = {}     # page -> time step when loaded into memory
    
    page_faults = 0
    page_hits = 0
    results = []

    for t, page in enumerate(reference_string):
        frequencies[page] = frequencies.get(page, 0) + 1
        evicted = None
        victim_slot = None
        reason = ""

        if page in physical_frames:
            status = "Hit"
            page_hits += 1
            victim_slot = physical_frames.index(page)
            reason = f"Page {page} found in Frame {victim_slot + 1} (Hit count: {frequencies[page]})."
        else:
            status = "Fault"
            page_faults += 1
            
            # Check for an empty slot first
            if None in physical_frames:
                victim_slot = physical_frames.index(None)
                physical_frames[victim_slot] = page
                arrival_time[page] = t
                reason = f"Page {page} loaded into empty Frame {victim_slot + 1}."
            else:
                # Find page with minimum frequency; tie-breaker: oldest arrival time (FIFO)
                victim_page = min(
                    physical_frames,
                    key=lambda p: (frequencies.get(p, 0), arrival_time.get(p, 0))
                )
                victim_slot = physical_frames.index(victim_page)
                evicted = victim_page
                reason = (
                    f"Page {victim_page} evicted from Frame {victim_slot + 1} "
                    f"(Freq: {frequencies[victim_page]}). Replaced by Page {page}."
                )
                
                # Update frames
                physical_frames[victim_slot] = page
                arrival_time[page] = t

        # Active pages currently in frames (filtered of None for compatibility)
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
