import os
import sys
import time
import fcntl
import subprocess
import hashlib

from typing import List, Dict
from pathlib import Path

from helper.config import *

def pr_info(msg: str) -> None:
    if LOG_INFO:
        print(f"\033[1;36m[INFO]\033[0m {msg}")

def pr_error(msg: str) -> None:
    if LOG_ERROR:
        print(f"\033[1;31m[ERR]\033[0m {msg}")
        print(f"\033[1;31m[ERR]\033[0m {msg}", file= sys.stderr)

def pr_fatal(msg: str) -> None:
    print(f"\033[1;35m[FATAL]\033[0m {msg}")
    print(f"\033[1;35m[FATAL]\033[0m {msg}", file= sys.stderr)

class FatalError(Exception):
    pass

def run_command(cmd: List[str], name: str = "") -> subprocess.Popen:
    try:
        proc = subprocess.Popen(
            cmd,
            stdin= subprocess.PIPE,
            stdout= subprocess.PIPE,
            stderr= None,
            text= True
        )
        fd = proc.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    except Exception as e:
        raise FatalError(f"Judge system error. ({e})")

    pr_info(f"Process '{name}' started. (pid: {proc.pid})")
    return proc

def check_process(proc: subprocess.Popen, name: str = "") -> bool:
    if proc.poll() is not None:
        pr_error(f"'{name}' unexpected terminated. ({proc.returncode})")
        return False
    return True

def assert_normal(proc: subprocess.Popen, name: str = ""):
    if proc.poll() is not None and proc.returncode != 0:
        raise FatalError(f"'{name}' should keep alive. ({proc.returncode})")

def wait_for_output(proc: subprocess.Popen, sync_str: str, timeout: int, name: str = "") -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            line = proc.stdout.readline()
            if line.strip() == sync_str:
                pr_info(f"'{name}' get expected output '{sync_str}'.")
                return True
        except BlockingIOError:
            pass
        
        assert_normal(proc, name)

        time.sleep(0.01)

    pr_error(f"'{name}' timed out, waiting for sync str '{sync_str}'.")
    return False

def wait_for_line(proc: subprocess.Popen, timeout: int, name: str = "") -> str:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            line = proc.stdout.readline()
            if len(line):
                return line.strip()
        except BlockingIOError:
            pass

        assert_normal(proc, name)

        time.sleep(0.01)

    pr_error(f"'{name}' timed out, waiting for a line.")
    return ""

def check_shm(proc: subprocess.Popen, name: str = "") -> bool:
    pid = proc.pid
    maps_path = Path(f"/proc/{pid}/maps")
    maps_content = maps_path.read_text()
    is_found = False

    for line in maps_content.splitlines():
        parts = line.split()
        if 's' in parts[1]:
            if len(parts) >= 6:
                filename = parts[5]
                if filename.startswith('[') or filename == '':
                    pr_error(f"Found unexpected shared memory region(s) in '{name}'.\n\n{maps_content}")
                    return False
    
                addr_range = parts[0].split('-')
                start_addr = int(addr_range[0], 16)
                end_addr = int(addr_range[1], 16)
                
                size = end_addr - start_addr
            
                if size != 1024 * 1024:
                    pr_error(f"Found a shared memory region in '{name}' w/ incorrect size. (!= 1 MB)")
                    return False

                if is_found:
                    pr_error(f"Found unexpected shared memory region(s) in '{name}'.\n\n{maps_content}")
                    return False
                else:
                    is_found = True
            else:
                pr_error(f"Found unexpected shared memory region(s) in '{name}'.\n\n{maps_content}")
                return False

    pr_info(f"'{name}' passed the shared memory check.")
    return True



def sha256(content: bytes) -> str:
    m = hashlib.sha256()
    m.update(content)
    return m.hexdigest()

def merkle_root(content: bytes) -> str:
    hashes = []
    for offset in range(0, len(content), 4096):
        segment_length = min(offset + 4096, len(content))
        hashes.append(
            sha256(content[offset:offset+segment_length])
        )
        
    while len(hashes) != 1:
        nxt_hashes = []
        for idx in range(0, len(hashes), 2):
            nxt_hashes.append(
                sha256((hashes[idx] + hashes[idx+1]).encode())
            )
        if len(hashes) % 2 == 1:
            nxt_hashes.append(hashes[-1])
        hashes = nxt_hashes
        
    return hashes[0]

def merkle_root_for_file(path: str) -> str:
    hashes = []
    with open(path, "rb") as f:
        while True:
            segment_content = f.read(4096)
            if not segment_content:
                break
            hashes.append(
                sha256(segment_content)
            )
        
    while len(hashes) != 1:
        nxt_hashes = []
        for idx in range(1, len(hashes), 2):
            nxt_hashes.append(
                sha256((hashes[idx-1] + hashes[idx]).encode())
            )
        if len(hashes) % 2 == 1:
            nxt_hashes.append(hashes[-1])
        hashes = nxt_hashes
        
    return hashes[0]

def check_threads(proc: subprocess.Popen, expected_nr: int, name: str = "") -> bool:
    pid = proc.pid
    task_dir = f"/proc/{pid}/task"

    try:
        nr_threads = len(os.listdir(task_dir))
    except Exception as e:
        pr_error(f"Failed to get thread number for '{name}'. ({e})")
        return False

    if nr_threads != expected_nr:
        pr_error(f"'{name}' thread number mismatch. (expected {expected_nr}, got {nr_threads})")
        return False

    pr_info(f"'{name}' has expected '{expected_nr}' threads.")
    return True
