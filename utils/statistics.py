def calculate_statistics(hits, faults, total_pages, mat_ns=100, pfst_ns=8_000_000):
    """
    Calculate comprehensive memory management statistics.
    
    Parameters:
    - hits (int): Number of page hits
    - faults (int): Number of page faults
    - total_pages (int): Total number of memory references
    - mat_ns (float): Memory Access Time in nanoseconds (default: 100 ns)
    - pfst_ns (float): Page Fault Service Time in nanoseconds (default: 8,000,000 ns = 8 ms)
    """
    hit_ratio = hits / total_pages if total_pages > 0 else 0.0
    fault_ratio = faults / total_pages if total_pages > 0 else 0.0
    emat_ns = (1.0 - fault_ratio) * mat_ns + fault_ratio * pfst_ns

    return {
        "hits": hits,
        "faults": faults,
        "total_pages": total_pages,
        "hit_ratio": hit_ratio,
        "fault_ratio": fault_ratio,
        "emat_ns": emat_ns,
        "mat_ns": mat_ns,
        "pfst_ns": pfst_ns
    }
