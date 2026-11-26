"""
Page size and other considerations (Unit 3: Virtual Memory).

Trade-off: small pages -> big page table, little internal fragmentation;
           large pages -> small page table, more internal fragmentation, larger TLB reach.
"""
import math


def page_size_analysis(process_bytes, page_sizes, pte_bytes=4, tlb_entries=64):
    """Overhead of storing a process of `process_bytes` bytes for each candidate page size."""
    if process_bytes <= 0:
        raise ValueError("Process size must be positive.")
    if pte_bytes <= 0 or tlb_entries <= 0:
        raise ValueError("PTE size and TLB entries must be positive.")
    rows = []
    for p in page_sizes:
        if p <= 0:
            raise ValueError("Page sizes must be positive.")
        pages = math.ceil(process_bytes / p)
        table = pages * pte_bytes
        frag = pages * p - process_bytes  # wasted bytes in the last page
        rows.append({
            "Page Size (B)": p,
            "Pages": pages,
            "Page Table (B)": table,
            "Internal Fragmentation (B)": frag,
            "Total Overhead (B)": table + frag,
            "TLB Reach (B)": tlb_entries * p,
        })
    return rows


def theoretical_optimal_page_size(process_bytes, pte_bytes=4):
    """Minimises page-table size + expected waste (p/2): p = sqrt(2 * s * e)."""
    return math.sqrt(2 * process_bytes * pte_bytes)
