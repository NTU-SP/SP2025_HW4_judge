import sys
import random

from helper.config import *
from helper.utils import *

NR_SUBSCRIBERS = 30
NR_PUBLISHERS = 30
CHANNEL_NAME = "ccc"

subscribers = [None] * NR_SUBSCRIBERS
publishers = [None] * NR_PUBLISHERS

def kill_procs(procs):
    for i in range(len(procs)):
        if procs[i] is not None:
            procs[i].kill()
            procs[i] = None

def kill_all_procs():
    kill_procs(subscribers)
    kill_procs(publishers)

nr_msgs_per_pub = [random.randint(3, 5) for _ in range(NR_PUBLISHERS)]
nr_msgs = sum(nr_msgs_per_pub)

try:
    for i in range(NR_SUBSCRIBERS):
        subscribers[i] = run_command([f"{BINARY_DIR}/sub", CHANNEL_NAME, str(nr_msgs)], f"subscriber{i}")
        if not wait_for_output(subscribers[i], SJOIN, MAX_TIMEOUT, f"subscriber{i}"):
            kill_all_procs()
            sys.exit(JUDGE_WA)

    for i in range(NR_PUBLISHERS):
        publishers[i] = run_command([f"{BINARY_DIR}/pub", CHANNEL_NAME, f"fakefile{i}", str(nr_msgs_per_pub[i] * 4096)], f"publisher{i}")
        if not wait_for_output(publishers[i], PJOIN, MAX_TIMEOUT, f"publisher{i}"):
            kill_all_procs()
            sys.exit(JUDGE_WA)
    
    pr_info(f"Each subscriber should receive {nr_msgs} messages")

    for i in range(NR_SUBSCRIBERS):
        if not wait_for_output(subscribers[i], "[SUBSCRIBER SYNC POINT]", MAX_TIMEOUT, f"subscriber{i}"):
            kill_all_procs()
            sys.exit(JUDGE_WA)

    kill_all_procs()

except Exception as e:
    kill_all_procs()
    pr_fatal(f"An unexpected error occurred during testing. ({e})")
    sys.exit(JUDGE_FATAL)

pr_info("OK! You passed this test case.")

