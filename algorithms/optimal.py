def optimal(reference_string, frame_count):
    """
    Optimal (MIN / Belady's) Page Replacement Algorithm.
    Replaces the page that will not be used for the longest period of time in the future.
    """
    physical_frames = [None] * frame_count
    load_time = {}  # tie-breaker if multiple pages are never used again
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
            reason = f"Page {page} found in Frame {victim_slot + 1}."
        else:
            status = "Fault"
            page_faults += 1

            # Check for an empty slot first
            if None in physical_frames:
                victim_slot = physical_frames.index(None)
                physical_frames[victim_slot] = page
                load_time[page] = t
                reason = f"Page {page} allocated to empty Frame {victim_slot + 1}."
            else:
                future = reference_string[t + 1:]
                next_uses = []

                for p in physical_frames:
                    if p in future:
                        next_uses.append((future.index(p), load_time.get(p, 0), p))
                    else:
                        next_uses.append((float('inf'), load_time.get(p, 0), p))

                # Farthest next use wins; if tie at infinity, oldest loaded page (FIFO)
                next_uses.sort(key=lambda item: (item[0], -item[1]), reverse=True)
                victim_page = next_uses[0][2]
                farthest_dist = next_uses[0][0]
                
                victim_slot = physical_frames.index(victim_page)
                evicted = victim_page
                
                if farthest_dist == float('inf'):
                    reason = f"Page {victim_page} in Frame {victim_slot + 1} is never used again in future; replaced by Page {page}."
                else:
                    reason = f"Page {victim_page} in Frame {victim_slot + 1} next used in {farthest_dist + 1} steps (farthest); replaced by Page {page}."

                physical_frames[victim_slot] = page
                load_time[page] = t

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
