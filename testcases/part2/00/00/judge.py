import sys

from helper.config import *
from helper.utils import *

proc1, proc2 = None, None

CHANNEL_NAME = "testtesttest"
FILE_NAME = "marigold"
FILE_PATH = f"testcase/{FILE_NAME}"
SRC_FILE_PATH = f"testcase/_{FILE_NAME}"

try:
    with open(SRC_FILE_PATH, "rb") as f:
        content = f.read()

    with open(FILE_PATH, "wb") as f:
        for _ in range(1024 * 1024 // len(content)):
            f.write(content)

    answer = f"[ANSWER] {FILE_NAME}: {merkle_root_for_file(FILE_PATH)}"

    proc1 = run_command([f"{BINARY_DIR}/merkle_subscriber", CHANNEL_NAME, "3"], "merkle_subscriber")

    if not wait_for_output(proc1, SJOIN, MAX_TIMEOUT, "merkle_subscriber"):
        proc1.kill()
        sys.exit(JUDGE_WA)

    proc2 = run_command([f"{BINARY_DIR}/pub", CHANNEL_NAME, FILE_PATH], "publisher")

    if not wait_for_output(proc2, PJOIN, MAX_TIMEOUT, "publisher"):
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
    pr_fatal(f"An unexpected error occurred during testing. ({e})")
    sys.exit(JUDGE_FATAL)

pr_info("OK! You passed this test case.")
