import sys

from helper.config import *
from helper.utils import *

proc1, proc2 = None, None

channel_name = "testtesttest"

answer = f"[ANSWER] marigold: {merkle_root_for_file("testcase/marigold")}"

try:
    proc1 = run_command([f"{BINARY_DIR}/merkle_subscriber", channel_name, "3"], "merkle_subscriber")

    if not wait_for_output(proc1, "The subscriber node has joined the channel.", MAX_TIMEOUT, "subscriber"):
        proc1.kill()
        sys.exit(JUDGE_WA)

    proc2 = run_command([f"{BINARY_DIR}/pub", channel_name, "testcase/marigold"], "pub")

    if not wait_for_output(proc2, "The publisher node has joined the channel.", MAX_TIMEOUT, "publisher"):
        proc1.kill()
        proc2.kill()
        sys.exit(JUDGE_WA)
        
    if not wait_for_output(proc1, answer, MAX_TIMEOUT, "merkle_subscriber"):
        proc1.kill()
        proc2.kill()
        sys.exit(JUDGE_WA)

    proc1.kill()
    proc1 = None
    proc2.kill()
    proc2 = None

except Exception as e:
    if proc1 is not None:
        proc1.kill()
    if proc2 is not None:
        proc2.kill()
    pr_error(f"An unexpected error occurred during testing. ({e})")
    sys.exit(JUDGE_FATAL)

pr_info("OK! You passed this test case.")

