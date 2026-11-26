
from algorithms.optimal import optimal

# Input
reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3]
frame_count = 3

# Run Optimal
results, hits, faults = optimal(reference_string, frame_count)

print("\nOPTIMAL PAGE REPLACEMENT")
print("-" * 60)

for step, result in enumerate(results, start=1):
    print(
        f"Step {step}: Page {result['Page']} | "
        f"Frames: {result['Frames']} | "
        f"Status: {result['Status']}"
    )

print("-" * 60)
print("Total Page Hits:", hits)
print("Total Page Faults:", faults)
print("Hit Ratio:", round(hits / len(reference_string), 2))
print("Fault Ratio:", round(faults / len(reference_string), 2))
