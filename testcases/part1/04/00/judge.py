import sys
import re

from helper.config import *
from helper.utils import *

proc1, proc2, proc3 = None, None, None

content = "だから風に吹かれていこう\nフィルムは用意したよ\n一生分の長さを ざっと115万キロ"

try:
    proc1 = run_command([f"{BINARY_DIR}/sub"], "subscriber1")

    if not wait_for_output(proc1, "The subscriber node has joined the channel.", MAX_TIMEOUT, "subscriber1"):
        proc1.kill()
        sys.exit(JUDGE_WA)

    proc2 = run_command([f"{BINARY_DIR}/sub"], "subscriber2")

    if not wait_for_output(proc2, "The subscriber node has joined the channel.", MAX_TIMEOUT, "subscriber2"):
        proc1.kill()
        proc2.kill()
        sys.exit(JUDGE_WA)

    proc3 = run_command([f"{BINARY_DIR}/pub"], "publisher")

    if not wait_for_output(proc3, "The publisher node has joined the channel.", MAX_TIMEOUT, "publisher"):
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)
    
    line_from_proc1 = wait_for_line(proc1, MAX_TIMEOUT, "subscriber1")
    if len(line_from_proc1) == 0:
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)

    hex_bytes = re.findall(r'\\x([0-9a-f]{2})', line_from_proc1)
    decoded_line_proc1 = bytes(int(h, 16) for h in hex_bytes).decode()

    if decoded_line_proc1 == content:
        pr_info("'subscriber1' received correct content")

    line_from_proc2 = wait_for_line(proc2, MAX_TIMEOUT, "subscriber1")
    if len(line_from_proc1) == 0:
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)

    hex_bytes = re.findall(r'\\x([0-9a-f]{2})', line_from_proc2)
    decoded_line_proc2 = bytes(int(h, 16) for h in hex_bytes).decode()

    if decoded_line_proc2 == content:
        pr_info("'subscriber2' received correct content")

    if not check_shm(proc1, "subscriber1"):
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)

    if not check_shm(proc2, "subscriber2"):
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)

    if not check_shm(proc3, "publisher"):
        proc1.kill()
        proc2.kill()
        proc3.kill()
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
        proc2.kill()
    pr_error(f"An unexpected error occurred during testing. ({e})")
    sys.exit(JUDGE_FATAL)

pr_info("OK! You passed this test case.")

