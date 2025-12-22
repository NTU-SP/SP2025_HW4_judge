# SP2025 Programming Assignment 4 Judge System

This repository contains the judge script and related resources for the SP2025 Programming Assignment 4.

## Quick Start

To begin the testing process, execute the script with your source directory as the argument:

```bash
./judge.sh <hw4 directory>
```

The script will guide you through the initial configuration and then run the testcases.

## Environment

Upon startup, you will be asked: `Configure your container engine (docker|none|custom)?`

| Option | Description |
| :----: | :---------- |
| `docker` | Use `docker` as your container engine. This guarantees that the toolchains match the official grading environment and provides isolation to prevent buggy programs from affecting your host system. |
| `none` | Run directly on your host. Results may vary due to differences in toolchains (`gcc`, `make`, `python` versions). |
| `custom` | Use an alternative container engine like `podman`. |

If using `docker`, ensure you have run `setup.sh` first to build the `sp_hw4` container image.

## Advanced Features

### Testcases

The `judge.sh` script is easy to understand. It iterates through the `testcases` directory and executes each testcase found within.

We encourage you to create and share your own testcases with your classmates! Ensuring your program performs correctly across diverse scenarios is the best way to guarantee a robust and bug-free implementation.

### IGNORE Mechanism

Some testcases, such as `p1-05-02`, involve a larger workload and may take a long time to complete.

If you want to skip specific testcases during frequent development cycles to save time, the judge exposes a simple bypass method. You can create an `IGNORE` file in the specific testcase directory:

```bash
# Skip the testcase p1-05-02
touch testcases/part1/05/02/IGNORE
```

Once the `IGNORE` file is detected, the judge will skip that testcase and exclude its points, allowing you to focus on other parts of your implementation.
