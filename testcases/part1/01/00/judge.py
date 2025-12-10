import sys

from helper.config import *
from helper.utils import *

proc1, proc2 = None, None

expected_outputs = [
    "name: kimiwarokkuwokikanai",
    "len: 1128",
    "total len: 2147483648",
    "offset: 7777",
    "hash: 2c9dbcc345220dabcb06a1ff8105655138e171fcd3f9f759120d226638076c9a",
    "1 1"
]

try:
    proc1 = run_command([f"{BINARY_DIR}/sub"], "subscriber")

    if not wait_for_output(proc1, "The subscriber node has joined the channel.", MAX_TIMEOUT, "subscriber"):
        proc1.kill()
        sys.exit(JUDGE_WA)

    proc2 = run_command([f"{BINARY_DIR}/pub"], "publisher")

    if not wait_for_output(proc2, "The publisher node has joined the channel.", MAX_TIMEOUT, "publisher"):
        proc1.kill()
        proc2.kill()
        sys.exit(JUDGE_WA)
    
    for expected_output in expected_outputs:
        if not wait_for_output(proc1, expected_output, MAX_TIMEOUT, "subscriber"):
            proc1.kill()
            proc2.kill()
            sys.exit(JUDGE_WA)

    if not check_shm(proc1, "subscriber"):
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

