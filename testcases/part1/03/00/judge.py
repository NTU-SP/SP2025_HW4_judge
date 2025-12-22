import sys
import random
import time

from helper.config import *
from helper.utils import *

proc1, proc2 = None, None

random.seed(time.time())

nr_msgs_1 = random.randint(70, 100)
nr_msgs_2 = 300 - nr_msgs_1
nr_msgs_3 = random.randint(3000, 5000)
nr_msgs_4 = random.randint(500000, 1000000)

nr_msgs = [nr_msgs_1, nr_msgs_2, nr_msgs_3, nr_msgs_4]
expected_names = [
    "bokuwanankaidatte",
    "nanjukkaidatte",
    "kimitodakiatte tewo",
    "tsunaidekisuwoshita"
]
expected_total_lengths = [n * 522 for n in nr_msgs]
expected_length = 522

try:
    proc1 = run_command([f"{BINARY_DIR}/sub"], "subscriber")

    if not wait_for_output(proc1, "The subscriber node has joined the channel.", MAX_TIMEOUT, "subscriber"):
        proc1.kill()
        sys.exit(JUDGE_WA)

    proc2 = run_command([f"{BINARY_DIR}/pub"] + list(map(str, nr_msgs)), "publisher")

    if not wait_for_output(proc2, "The publisher node has joined the channel.", MAX_TIMEOUT, "publisher"):
        proc1.kill()
        proc2.kill()
        sys.exit(JUDGE_WA)
    
    for i, nr_msg in enumerate(nr_msgs):
        recv_msgs = []
        for _ in range(nr_msg):
            line = wait_for_line(proc1, MAX_TIMEOUT, "subscriber")
            if len(line) == 0:
                proc1.kill()
                proc2.kill()
                sys.exit(JUDGE_WA)

            if random.random() < 0.001:
                if random.random() < 0.01:
                    if not check_shm(proc1, "subscriber"):
                        proc1.kill()
                        proc2.kill()
                        sys.exit(JUDGE_WA)

            outs = line.split(';')
            name = outs[0]
            length, total_length, offset, p1, p2 = map(int, outs[1:])
            if (name != expected_names[i] or
                total_length != expected_total_lengths[i] or
                length != expected_length or
                p1 != 1 or p2 != 1
            ):
                proc1.kill()
                proc2.kill()
                pr_error(f"Subscriber received an unexpected line. ('{line}')")
                sys.exit(JUDGE_WA)

            recv_msgs.append(offset)

        recv_msgs.sort()
        for j in range(1, len(recv_msgs)):
            if recv_msgs[j - 1] + expected_length != recv_msgs[j]:
                proc1.kill()
                proc2.kill()
                pr_error("Subscriber received out-of-order or missing messages.")
                sys.exit(JUDGE_WA)
        
        pr_info(f"OK! Successfully exchange {nr_msg} messages.")
        
        proc2.stdin.write("a")
        proc2.stdin.flush()
        if not wait_for_output(proc2, "[PUBLISHER SYNC WAKEUP]", MAX_TIMEOUT, "publisher"):
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

