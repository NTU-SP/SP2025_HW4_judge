import sys

from helper.config import *
from helper.utils import *

proc1, proc2, proc3 = None, None, None

channel_name = "oO0oO0O0oO0o"

try:
    with open("testcase/_sekaigaowaru", "rb") as f:
        content = f.read()

    with open("testcase/sekaigaowaru", "wb") as f:
        for _ in range(1024 * 1024 // len(content)):
            f.write(content)

    with open("testcase/urawoagiakes", "wb") as f:
        for _ in range(1024 * 1024 // len(content)):
            f.write(content[::-1])

    answer1 = f"[ANSWER] sekaigaowaru: {merkle_root_for_file("testcase/sekaigaowaru")}"
    answer2 = f"[ANSWER] urawoagiakes: {merkle_root_for_file("testcase/urawoagiakes")}"

    proc1 = run_command([f"{BINARY_DIR}/merkle_subscriber", channel_name, "2"], "merkle_subscriber")

    if not wait_for_output(proc1, "The subscriber node has joined the channel.", MAX_TIMEOUT, "merkle_subscriber"):
        proc1.kill()
        sys.exit(JUDGE_WA)

    proc2 = run_command([f"{BINARY_DIR}/pub", channel_name, "testcase/sekaigaowaru"], "pub1")

    if not wait_for_output(proc2, "The publisher node has joined the channel.", MAX_TIMEOUT, "pub1"):
        proc1.kill()
        proc2.kill()
        sys.exit(JUDGE_WA)
    
    proc3 = run_command([f"{BINARY_DIR}/pub", channel_name, "testcase/urawoagiakes"], "pub2")

    if not wait_for_output(proc3, "The publisher node has joined the channel.", MAX_TIMEOUT, "pub2"):
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)
    
    proc2.stdin.write("1\n")
    proc2.stdin.flush()
    proc3.stdin.write("1\n")
    proc3.stdin.flush()

    line1 = wait_for_line(proc1, MAX_TIMEOUT, "merkle_subscriber")
    if len(line1) == 0:
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)

    line2 = wait_for_line(proc1, MAX_TIMEOUT, "merkle_subscriber")
    if len(line2) == 0:
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)

    pr_info(f"'merkle_subscriber' received {line1}")
    pr_info(f"'merkle_subscriber' received {line2}")

    if line1 == answer1:
        if line2 != answer2:
            proc1.kill()
            proc2.kill()
            proc3.kill()
            pr_error(f"'merkle_subscriber' generated incorrect Merkle root '{line2}'.")
            sys.exit(JUDGE_WA)
    elif line1 == answer2:
        if line2 != answer1:
            proc1.kill()
            proc2.kill()
            proc3.kill()
            pr_error(f"'merkle_subscriber' generated incorrect Merkle root '{line2}'.")
            sys.exit(JUDGE_WA)
    else:
        proc1.kill()
        proc2.kill()
        proc3.kill()
        pr_error(f"'merkle_subscriber' generated incorrect Merkle root '{line1}'.")
        sys.exit(JUDGE_WA)

    proc1.kill()
    proc1 = None
    proc2.kill()
    proc2 = None
    proc3.kill()
    proc3 = None

except Exception as e:
    if proc1 is not None:
        proc1.kill()
    if proc2 is not None:
        proc2.kill()
    if proc3 is not None:
        proc3.kill()
    pr_fatal(f"An unexpected error occurred during testing. ({e})")
    sys.exit(JUDGE_FATAL)

pr_info("OK! You passed this test case.")

