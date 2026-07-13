"""
file_pointer_demo_generic.py

Demonstrates how a file object's internal read pointer works in Python,
and why looping over the same open file twice only "does something" the
first time.

Usage in Google Colab:
    !python file_pointer_demo_generic.py path/to/your_file.txt
or:
    import file_pointer_demo_generic
    file_pointer_demo_generic.run_original("path/to/your_file.txt")
"""

import sys


# --- fallback sample file, used only if no filename is given --------------
SAMPLE_FILE = "sample.txt"


def make_sample_file():
    with open(SAMPLE_FILE, "w") as f:
        f.write("apple\nbanana\ncherry\ndate\n")


# --- original behavior (pointer only moves forward) -----------------------
def run(filename):
    print(f"=== run_original({filename!r}) ===")
    fileIn = open(filename, "r")

    print("First run:")
    for line in fileIn:
        print(line.strip())

    print("Second run:")
    for line in fileIn:          # pointer is already at end of file here
        print(line.strip())

    fileIn.close()
    print("Closed file, the end!")
    print()


# --- fix #1: rewind the pointer with seek(0) -------------------------------
def run_with_seek(filename):
    print(f"=== run_with_seek({filename!r}) ===")
    fileIn = open(filename, "r")

    print("First run:")
    for line in fileIn:
        print(line.strip())

    fileIn.seek(0)  # move the pointer back to the start of the file

    print("Second run:")
    for line in fileIn:
        print(line.strip())

    fileIn.close()
    print("Closed file, the end!")
    print()


# --- fix #2: read all lines once, loop over the list twice ----------------
def run_with_list(filename):
    print(f"=== run_with_list({filename!r}) ===")
    with open(filename, "r") as fileIn:
        all_lines = fileIn.readlines()  # pointer moves to end, but we kept the data

    print("First run:")
    for line in all_lines:
        print(line.strip())

    print("Second run:")
    for line in all_lines:
        print(line.strip())

    print("Closed file, the end!")
    print()


if __name__ == "__main__":
    # Use a filename passed on the command line, e.g.:
    #   python file_pointer_demo_generic.py mytext.txt
    # Otherwise fall back to a generated sample file.
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        make_sample_file()
        target_file = SAMPLE_FILE

    run_original(target_file)
    run_with_seek(target_file)
    run_with_list(target_file)
