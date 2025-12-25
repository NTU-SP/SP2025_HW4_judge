import sys
import re

from helper.config import *
from helper.utils import *

NR_PUBLISHERS = 64
CHANNEL_NAME = "iikoninantenaranaide"
FILE_NAME = "nichijyou"
FILE_PATH = f"testcase/{FILE_NAME}"
SRC_FILE_PATH = f"testcase/_{FILE_NAME}"

subscriber = None
publishers = [None] * NR_PUBLISHERS

def kill_procs(procs):
    for i in range(len(procs)):
        if procs[i] is not None:
            procs[i].kill()
            procs[i] = None

def kill_all_procs():
    if subscriber is not None:
        subscriber.kill()
    kill_procs(publishers)

try:
    with open(SRC_FILE_PATH, "rb") as f:
        content = f.read()

    with open(FILE_PATH, "wb") as f:
        for _ in range(1024 * 1024 // len(content)):
            f.write(content)

    answer_reg = rf"\[ANSWER\] {FILE_NAME}(\d+): {merkle_root_for_file(FILE_PATH)}"

    subscriber = run_command([f"{BINARY_DIR}/merkle_subscriber", CHANNEL_NAME, "8"], "merkle_subscriber")

    if not wait_for_output(subscriber, SJOIN, MAX_TIMEOUT, "merkle_subscriber"):
        subscriber.kill()
        sys.exit(JUDGE_WA)

    for i in range(NR_PUBLISHERS):
        publishers[i] = run_command([f"{BINARY_DIR}/pub", CHANNEL_NAME, FILE_PATH, str(i)], f"pub{i}")
        if not wait_for_output(publishers[i], PJOIN, MAX_TIMEOUT, f"pub{i}"):
            kill_all_procs()
            sys.exit(JUDGE_WA)

    for _ in range(NR_PUBLISHERS):
        line = wait_for_line(subscriber, MAX_TIMEOUT, "merkle_subscriber")
        if len(line) == 0:
            kill_all_procs()
            sys.exit(JUDGE_WA)
        m = re.match(answer_reg, line)
        if m:
            extracted_id = int(m.group(1))
            pr_info(f"Received valid output from subscriber. (id: {extracted_id})")
        else:
            pr_error(f"Received unexpected output from subscriber. ('{line}')")
            kill_all_procs()
            sys.exit(JUDGE_WA)

    for i in range(NR_PUBLISHERS):
        if not wait_for_output(publishers[i], "[PUBLISHER SYNC END]", MAX_TIMEOUT, f"pub{i}"):
            kill_all_procs()
            sys.exit(JUDGE_WA)
        publishers[i] = None

    for i in range(NR_PUBLISHERS):
        publishers[i] = run_command([f"{BINARY_DIR}/pub", CHANNEL_NAME, FILE_PATH, str(NR_PUBLISHERS+i)], f"pub{NR_PUBLISHERS+i}")
        if not wait_for_output(publishers[i], PJOIN, MAX_TIMEOUT, f"pub{NR_PUBLISHERS+i}"):
            kill_all_procs()
            sys.exit(JUDGE_WA)

    for _ in range(NR_PUBLISHERS):
        line = wait_for_line(subscriber, MAX_TIMEOUT, "merkle_subscriber")
        if len(line) == 0:
            kill_all_procs()
            sys.exit(JUDGE_WA)
        m = re.match(answer_reg, line)
        if m:
            extracted_id = int(m.group(1))
            pr_info(f"Received valid output from subscriber. (id: {extracted_id})")
        else:
            pr_error(f"Received unexpected output from subscriber. ('{line}')")
            kill_all_procs()
            sys.exit(JUDGE_WA)
    
    kill_all_procs()

except Exception as e:
    kill_all_procs()
    pr_fatal(f"An unexpected error occurred during testing. ({e})")
    sys.exit(JUDGE_FATAL)

pr_info("OK! You passed this test case.")

