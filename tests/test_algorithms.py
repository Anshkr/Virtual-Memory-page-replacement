"""Run from the project root:  python -m pytest -v"""
import pytest

from algorithms.fifo import fifo
from algorithms.lru import lru
from algorithms.optimal import optimal
from algorithms.lfu import lfu
from algorithms.clock import clock
from algorithms.allocation import equal_allocation, proportional_allocation, simulate_local, simulate_global
from algorithms.thrashing import working_set_sizes, analyze_thrashing, recommended_frames, slowdown_factor
from algorithms.page_size import page_size_analysis, theoretical_optimal_page_size
from algorithms.segmentation import demand_segmentation
from utils.statistics import calculate_statistics

ALGOS = {"FIFO": fifo, "LRU": lru, "Optimal": optimal, "LFU": lfu, "Clock": clock}
TEXTBOOK = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
BELADY = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


def faults(name, seq, frames):
    return ALGOS[name](seq, frames)[2]


# ---------------- normal cases ----------------
@pytest.mark.parametrize("name,expected", [("FIFO", 15), ("LRU", 12), ("Optimal", 9), ("LFU", 13), ("Clock", 14)])
def test_textbook_three_frames(name, expected):
    assert faults(name, TEXTBOOK, 3) == expected


@pytest.mark.parametrize("name", ALGOS)
def test_hits_plus_faults_equals_length(name):
    _, hits, flt = ALGOS[name](TEXTBOOK, 3)
    assert hits + flt == len(TEXTBOOK)


def test_optimal_is_never_worse():
    for seq in (TEXTBOOK, BELADY, [1, 2, 3, 2, 1, 2, 3, 2, 1, 4, 5, 4, 5, 1, 2, 3]):
        for f in (1, 2, 3, 4):
            best = faults("Optimal", seq, f)
            assert all(best <= faults(n, seq, f) for n in ALGOS)


def test_belady_anomaly_fifo_and_lru_immunity():
    assert faults("FIFO", BELADY, 3) == 9 and faults("FIFO", BELADY, 4) == 10
    lru_curve = [faults("LRU", BELADY, f) for f in range(1, 8)]
    assert lru_curve == sorted(lru_curve, reverse=True)


# ---------------- boundary cases ----------------
@pytest.mark.parametrize("name", ALGOS)
def test_boundaries(name):
    assert faults(name, [1, 2, 1, 3, 1, 2], 1) == 6      # single frame
    assert faults(name, [5], 3) == 1                      # single reference
    assert faults(name, [4, 4, 4, 4, 4], 3) == 1          # all identical
    assert faults(name, [1, 2, 3, 1, 2, 3], 10) == 3      # frames > distinct pages
    assert faults(name, [1, 2, 3, 4, 5, 6], 3) == 6       # all distinct


def test_statistics_and_zero_total():
    s = calculate_statistics(5, 15, 20, 100, 8_000_000)
    assert s["fault_ratio"] == 0.75 and round(s["emat_ns"]) == 6_000_025
    z = calculate_statistics(0, 0, 0)
    assert z["hit_ratio"] == 0.0 and z["fault_ratio"] == 0.0


# ---------------- allocation of frames ----------------
def test_equal_and_proportional_allocation():
    assert equal_allocation(9, 3) == [3, 3, 3]
    assert equal_allocation(10, 3) == [4, 3, 3]
    alloc = proportional_allocation(62, [10, 127])      # Silberschatz example
    assert sum(alloc) == 62 and alloc == [5, 57]
    assert all(a >= 1 for a in proportional_allocation(4, [1, 1, 100]))


def test_allocation_invalid_inputs():
    with pytest.raises(ValueError):
        equal_allocation(2, 3)
    with pytest.raises(ValueError):
        proportional_allocation(5, [3, 0])


def test_local_and_global_simulation_consistent():
    procs = [[1, 2, 3, 1, 2, 3], [7, 8, 7, 8, 7, 8]]
    local = simulate_local(procs, [3, 2], lru)
    assert [r["faults"] for r in local] == [3, 2]
    glob = simulate_global(procs, 5, lru)
    assert [r["faults"] for r in glob] == [3, 2]
    assert sum(r["frames"] for r in glob) == 5


# ---------------- thrashing ----------------
def test_thrashing_detection():
    rows = analyze_thrashing(BELADY, lru, 6, 100, 8_000_000, threshold=0.5)
    assert rows[0]["Thrashing"] and rows[0]["Fault Ratio"] == 1.0
    assert recommended_frames(rows) == 5
    assert slowdown_factor(0.0, 100, 8_000_000) == 1.0


def test_no_false_thrashing_for_compulsory_misses():
    rows = analyze_thrashing([5], lru, 3, 100, 8_000_000, threshold=0.5)
    assert not any(r["Thrashing"] for r in rows)   # one page: its single fault is unavoidable


def test_working_set_sizes():
    assert working_set_sizes([1, 2, 1, 3, 3], 3) == [1, 2, 2, 3, 2]
    with pytest.raises(ValueError):
        working_set_sizes([1], 0)


# ---------------- page size ----------------
def test_page_size_tradeoff():
    rows = page_size_analysis(10_000, [1024, 4096], pte_bytes=4, tlb_entries=64)
    assert rows[0]["Pages"] == 10 and rows[0]["Internal Fragmentation (B)"] == 240
    assert rows[1]["Pages"] == 3 and rows[1]["Page Table (B)"] == 12
    assert rows[1]["TLB Reach (B)"] == 64 * 4096
    assert round(theoretical_optimal_page_size(1_024_000, 4)) == 2862
    with pytest.raises(ValueError):
        page_size_analysis(0, [1024])


# ---------------- demand segmentation ----------------
def test_demand_segmentation_lru_and_errors():
    sizes = {0: 400, 1: 250, 2: 300}
    res, hits, flt = demand_segmentation([0, 1, 0, 2, 1], sizes, 700, "LRU")
    assert (hits, flt) == (1, 4)
    assert res[3]["Evicted"] == [1] and max(r["Used"] for r in res) <= 700
    with pytest.raises(ValueError):
        demand_segmentation([9], sizes, 700)
    with pytest.raises(ValueError):
        demand_segmentation([0], sizes, 100)
