def clock(reference_string, frame_count):
    """
    Clock (Second Chance) Page Replacement Algorithm.
    Maintains a circular buffer of frames with a reference bit (use bit).
    """
    physical_frames = [None] * frame_count
    reference_bits = [0] * frame_count
    hand = 0  # Clock hand pointer
    
    page_faults = 0
    page_hits = 0
    results = []

    for page in reference_string:
        evicted = None
        victim_slot = None
        reason = ""

        if page in physical_frames:
            status = "Hit"
            page_hits += 1
            victim_slot = physical_frames.index(page)
            reference_bits[victim_slot] = 1  # Give second chance
            reason = f"Page {page} found in Frame {victim_slot + 1}. Reference bit set to 1."
        else:
            status = "Fault"
            page_faults += 1
            
            # Check for empty frame first
            if None in physical_frames:
                victim_slot = physical_frames.index(None)
                physical_frames[victim_slot] = page
                reference_bits[victim_slot] = 1
                hand = (victim_slot + 1) % frame_count
                reason = f"Page {page} loaded into empty Frame {victim_slot + 1}. Hand at Frame {hand + 1}."
            else:
                # Rotate clock hand looking for reference bit == 0
                cleared_slots = []
                while True:
                    if reference_bits[hand] == 0:
                        victim_slot = hand
                        victim_page = physical_frames[victim_slot]
                        evicted = victim_page
                        
                        physical_frames[victim_slot] = page
                        reference_bits[victim_slot] = 1
                        hand = (hand + 1) % frame_count
                        
                        extra = f" (Cleared ref bits on slots: {[s+1 for s in cleared_slots]})" if cleared_slots else ""
                        reason = (
                            f"Evicted Page {victim_page} from Frame {victim_slot + 1} (Ref bit was 0). "
                            f"Loaded Page {page}. Hand advanced to Frame {hand + 1}.{extra}"
                        )
                        break
                    else:
                        reference_bits[hand] = 0  # Second chance used
                        cleared_slots.append(hand)
                        hand = (hand + 1) % frame_count

        active_frames = [p for p in physical_frames if p is not None]

        results.append({
            "Page": page,
            "Frames": active_frames,
            "PhysicalFrames": list(physical_frames),
            "Status": status,
            "Evicted": evicted,
            "VictimSlot": victim_slot,
            "Reason": reason,
            "ClockHand": hand,
            "ReferenceBits": list(reference_bits)
        })

    return results, page_hits, page_faults
