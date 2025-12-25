import sys
import random

from helper.config import *
from helper.utils import *

proc1, proc2 = None, None

CHANNEL_NAME = "shikatanaiyo"

try:
    nr_threads = random.randint(5, 32)

    proc1 = run_command([f"{BINARY_DIR}/merkle_subscriber", CHANNEL_NAME, str(nr_threads)], "merkle_subscriber")

    if not wait_for_output(proc1, SJOIN, MAX_TIMEOUT, "merkle_subscriber"):
        proc1.kill()
        sys.exit(JUDGE_WA)

    if not check_threads(proc1, nr_threads + 1, "merkle_subscriber"):
        proc1.kill()
        sys.exit(JUDGE_WA)

    proc2 = run_command([f"{BINARY_DIR}/pub", CHANNEL_NAME], "publisher")

    if not wait_for_output(proc2, PJOIN, MAX_TIMEOUT, "publisher"):
        proc1.kill()
        proc2.kill()
        sys.exit(JUDGE_WA)
        
    for _ in range(nr_threads):
        line = wait_for_line(proc1, MAX_TIMEOUT, "merkle_subscriber")
        if len(line) == 0:
            proc1.kill()
            proc2.kill()
            sys.exit(JUDGE_WA)

        outs = line.split(':')

        if len(outs) != 2:
            proc1.kill()
            proc2.kill()
            pr_error(f"Subscriber received an unexpected line. ('{line}')")
            sys.exit(JUDGE_WA)

        tid = outs[1]
        pr_info(f"OK, '{tid}' thread is working.")

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
