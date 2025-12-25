import sys

from helper.config import *
from helper.utils import *

proc1, proc2 = None, None

CHANNEL_NAME = "koibitoninaritai"

try:
    proc1 = run_command([f"{BINARY_DIR}/merkle_subscriber", CHANNEL_NAME, "1"], "merkle_subscriber")

    if not wait_for_output(proc1, SJOIN, MAX_TIMEOUT, "merkle_subscriber"):
        proc1.kill()
        sys.exit(JUDGE_WA)

    proc2 = run_command([f"{BINARY_DIR}/pub", CHANNEL_NAME], "publisher")

    if not wait_for_output(proc2, PJOIN, MAX_TIMEOUT, "publisher"):
        proc1.kill()
        proc2.kill()
        sys.exit(JUDGE_WA)
        
    if not wait_for_output(proc1, "[INTERNAL TASK]", MAX_TIMEOUT, "merkle_subscriber"):
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
    pr_fatal(f"An unexpected error occurred during testing. ({e})")
    sys.exit(JUDGE_FATAL)

pr_info("OK! You passed this test case.")
