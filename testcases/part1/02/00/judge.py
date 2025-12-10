import sys
import random
import time

from helper.config import *
from helper.utils import *

proc1, proc2 = None, None

random.seed(time.time())
nr_msgs = random.randint(70, 100)
recv_msgs = []
expected_name = "watashiwaasagakirai"
expected_length = 522
expected_total_length = nr_msgs * 522

try:
    proc1 = run_command([f"{BINARY_DIR}/sub"], "subscriber")

    if not wait_for_output(proc1, "The subscriber node has joined the channel.", MAX_TIMEOUT, "subscriber"):
        proc1.kill()
        sys.exit(JUDGE_WA)

    proc2 = run_command([f"{BINARY_DIR}/pub", f"{nr_msgs}"], "publisher")

    if not wait_for_output(proc2, "The publisher node has joined the channel.", MAX_TIMEOUT, "publisher"):
        proc1.kill()
        proc2.kill()
        sys.exit(JUDGE_WA)
    
    for _ in range(nr_msgs):
        line = wait_for_line(proc1, MAX_TIMEOUT, "subscriber")
        if len(line) == 0:
            proc1.kill()
            proc2.kill()
            sys.exit(JUDGE_WA)
        outs = line.split(';')
        name = outs[0]
        length, total_length, offset, p1, p2 = map(int, outs[1:])
        if (name != expected_name or
            total_length != expected_total_length or
            length != expected_length or
            p1 != 1 or p2 != 1
        ):
            proc1.kill()
            proc2.kill()
            sys.exit(JUDGE_WA)
        recv_msgs.append(offset)

    if not check_shm(proc1, "subscriber"):
        proc1.kill()
        proc2.kill()
        sys.exit(JUDGE_WA)
    
    recv_msgs.sort()
    for i in range(1, len(recv_msgs)):
        if recv_msgs[i - 1] + expected_length != recv_msgs[i]:
            proc1.kill()
            proc2.kill()
            sys.exit(JUDGE_WA)

    pr_info(f"OK! Successfully exchange {nr_msgs} messages.")

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

