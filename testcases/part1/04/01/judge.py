import sys

from helper.config import *
from helper.utils import *

proc1, proc2, proc3 = None, None, None

name1 = "hyakujyugomankiro"
name2 = "aitokakoitoka"
content1 = "だから風に吹かれていこう\nフィルムは用意したよ\n一生分の長さを ざっと115万キロ"
content2 = "愛とか恋とかの言葉で片付けられないくらいの\n愛してるが 溢れ出して 止まらない想い"
hash1 = sha256(content1.encode())
hash2 = sha256(content2.encode())

try:
    proc1 = run_command([f"{BINARY_DIR}/sub"], "subscriber")

    if not wait_for_output(proc1, SJOIN, MAX_TIMEOUT, "subscriber"):
        proc1.kill()
        sys.exit(JUDGE_WA)

    proc2 = run_command([f"{BINARY_DIR}/pub1"], "publisher1")

    if not wait_for_output(proc2, PJOIN, MAX_TIMEOUT, "publisher1"):
        proc1.kill()
        proc2.kill()
        sys.exit(JUDGE_WA)

    proc3 = run_command([f"{BINARY_DIR}/pub2"], "publisher2")

    if not wait_for_output(proc3, PJOIN, MAX_TIMEOUT, "publisher2"):
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)
    

    line1 = wait_for_line(proc1, MAX_TIMEOUT, "subscriber")
    if len(line1) == 0:
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)

    line2 = wait_for_line(proc1, MAX_TIMEOUT, "subscriber")
    if len(line2) == 0:
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)

    pr_info(f"'subscriber' received {line1}")
    pr_info(f"'subscriber' received {line2}")

    if line1 == f"{name1}:{hash1}":
        if line2 != f"{name2}:{hash2}":
            proc1.kill()
            proc2.kill()
            proc3.kill()
            pr_error("Subscriber received incorrect content.")
            sys.exit(JUDGE_WA)
    elif line1 == f"{name2}:{hash2}":
        if line2 != f"{name1}:{hash1}":
            proc1.kill()
            proc2.kill()
            proc3.kill()
            pr_error("Subscriber received incorrect content.")
            sys.exit(JUDGE_WA)
    else:
        proc1.kill()
        proc2.kill()
        proc3.kill()
        pr_error("Subscriber received incorrect content.")
        sys.exit(JUDGE_WA)


    if not check_shm(proc1, "subscriber"):
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)

    if not check_shm(proc2, "publisher1"):
        proc1.kill()
        proc2.kill()
        proc3.kill()
        sys.exit(JUDGE_WA)

    if not check_shm(proc3, "publisher2"):
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
        proc3.kill()
    pr_fatal(f"An unexpected error occurred during testing. ({e})")
    sys.exit(JUDGE_FATAL)

pr_info("OK! You passed this test case.")

