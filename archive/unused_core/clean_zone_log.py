import os

INPUT_FILE = "reports/zone_transition_log.csv"
OUTPUT_FILE = "reports/zone_transition_log_cleaned.csv"
EXPECTED_FIELDS = 4

def clean_zone_transition_log(input_path, output_path, expected_fields=4):
    if not os.path.exists(input_path):
        print(f"[❌] File not found: {input_path}")
        return

    with open(input_path, "r") as infile:
        lines = infile.readlines()

    good_lines = []
    bad_lines = []

    for i, line in enumerate(lines, start=1):
        if line.count(",") == expected_fields - 1:
            good_lines.append(line)
        else:
            bad_lines.append((i, line.strip()))

    with open(output_path, "w") as outfile:
        outfile.writelines(good_lines)

    print(f"[✅] Cleaned log saved to: {output_path}")
    print(f"[📄] Valid rows kept: {len(good_lines)}")
    if bad_lines:
        print(f"[⚠️] Skipped {len(bad_lines)} malformed rows:")
        for idx, bad in bad_lines:
            print(f"  Line {idx}: {bad}")

if __name__ == "__main__":
    clean_zone_transition_log(INPUT_FILE, OUTPUT_FILE)
