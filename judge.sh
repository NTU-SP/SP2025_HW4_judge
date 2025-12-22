#!/bin/bash

CE="docker"
CI="sp_hw4"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
LRED='\033[1;31m'
LGREEN='\033[1;32m'
LYELLOW='\033[1;33m'
LBLUE='\033[1;34m'
LPURPLE='\033[1;35m'
LCYAN='\033[1;36m'
LWHITE='\033[1;37m'
NC='\033[0m'

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <hw4 directory>"
    exit 1;
fi

SRCDIR="$1"

if [[ (! -d "$SRCDIR/src/part1") || (! -d "$SRCDIR/src/part2") ]]; then
    echo -e "${LRED}[ERR]${NC} Your directory structure seems corrupted."
    exit 1
fi

P1DIR="$SRCDIR/src/part1"
P2DIR="$SRCDIR/src/part2"

echo -e "${LPURPLE}"
echo -e "############################################################"
echo -e "#                                                          #"
echo -e "#                  HW4 JUDGE SYSTEM START                  #"
echo -e "#                                                          #"
echo -e "############################################################"
echo -e "${NC}"

echo -e -n "\n${LWHITE}[ASK]${NC} Configure your container engine (docker|none|custom)? [Default: docker] "
read ce
if [[ -n "$ce" ]]; then CE="$ce"; fi

UC=1
if [[ "$ce" == "none" ]]; then
    UC=0
    echo -e "\n${LYELLOW}[WAR]${NC} Container disabled. The toolchain may differ from actual judge."
    echo -e "${LYELLOW}[WAR]${NC} Buggy programs that mess up the system cannot be recovered."
fi

if [[ $UC -eq 1 ]]; then
    echo -e "\n${LCYAN}[INFO]${NC} Your container engine is set to '$CE'."
    $CE -v > /dev/null 2>&1
    if [[ $? -ne 0 ]]; then
        echo -e "\n${LRED}[ERR]${NC} \`$CE -v\` returns an error."
        exit 1
    fi

    if [[ -z "$($CE image ls -q $CI)" ]]; then
        echo -e "\n${LRED}[ERR]${NC} \`$CE image ls -q $CI\` returns empty."
        echo -e "${LRED}[ERR]${NC} Please run 'setup.sh' firstly or check your container engine '$CE' again."
        exit 1
    fi
fi

ulimit -n 2048 > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    hlimit="$(ulimit -Hn)"
    echo -e "\n${LYELLOW}[WAR]${NC} Failed to set \`ulimit -n 2048\`."
    echo -e "${LYELLOW}[WAR]${NC} The actual judge would use a higher limit, which could cause different results."
fi

cd "$(dirname "$0")"

RDIR="$(pwd)"

WDIR="workdir"
WTDIR="workdir_template"
BDIR="build"
LOGDIR="logs"

TENTRY="judge.py"
TLOG="judge.log"

PART1_BATCHES=(testcases/part1/*)
PART2_BATCHES=(testcases/part2/*)

function run() {
    if [[ $UC -eq 1 ]]; then
        $CE run -it --rm -v "$(realpath $WDIR)":/judge:z $CI /bin/bash -c "$@"
    else
        (cd $WDIR && /bin/bash -c "$@")
    fi
}

function add() {
    awk "BEGIN {print $1 + $2}"
}

total_score=0
final_score=0

for batch_path in "${PART1_BATCHES[@]}"; do
    for t in "$batch_path"/*; do
        if [[ -f "$t/points" ]]; then
            total_score=$(add "$total_score" "$(cat "$t/points")")
        fi
    done
done


for batch_path in "${PART2_BATCHES[@]}"; do
    for t in "$batch_path"/*; do
        if [[ -f "$t/points" ]]; then
            total_score=$(add "$total_score" "$(cat "$t/points")")
        fi
    done
done

[[ ! -d "$LOGDIR" ]] && mkdir "$LOGDIR"

echo -e "\n${LGREEN}=================== Testcases for part1 ====================${NC}"

for batch_path in "${PART1_BATCHES[@]}"; do
    batch_num="$(basename "$batch_path")"

    echo -e "\n${LYELLOW}=================== Processing batch $batch_num ====================${NC}"

    TESTCASES=("$batch_path"/*)
    batch_failed=0
    total_score_per_batch=0
    final_score_per_batch=0
    failed_tests=()

    for testcase_path in "${TESTCASES[@]}"; do

        if [[ -f "$testcase_path/points" ]]; then
            cur_score=$(cat "$testcase_path/points")
        else
            cur_score=0
        fi

        total_score_per_batch=$(add "$total_score_per_batch" "$cur_score")
        testcase_num="$(basename "$testcase_path")"

        echo -e "\n${LBLUE}------------------ Running testcase $batch_num-$testcase_num ------------------${NC}\n"

        if [[ -f "$testcase_path/description" ]]; then
            echo -e "${LWHITE}-------------- Description for testcase ${batch_num}-${testcase_num} --------------${NC}\n"
            cat "$testcase_path/description"
            echo ""
        fi


        echo -e "${LWHITE}---------------------- Script output -----------------------${NC}\n"

        if [[ -f "$testcase_path/IGNORE" ]]; then
            echo -e "${LCYAN}[INFO]${NC} Testcase $batch_num-$testcase_num is ignored."
            continue
        fi

        cp -r "$WTDIR" "$WDIR"
        cp -r "$testcase_path" "$WDIR/testcase"
        mv "$WDIR/testcase/$TENTRY" "$WDIR/$TENTRY" > /dev/null 2>&1
        cp -r "$P1DIR" "$WDIR/src"

        run "make P1=src P2=testcase/src > /dev/null 2>&1"
        # run "make P1=src P2=testcase/src"
        if [[ $? -ne 0 ]]; then
            echo -e "${LRED}[FAIL]${NC} Compilation error."
            batch_failed=1
            failed_tests+=("$testcase_num")
            rm -rf "$WDIR"
            continue
        fi

        if [[ ! -f "$WDIR/$TENTRY" ]]; then
            echo -e "${LCYAN}[INFO]${NC} '$TENTRY' not found in testcase $batch_num-$testcase_num."
        else
            run "python3 $TENTRY 2>$TLOG"
        fi

        rc="$?"
        if [[ $rc -ne 0 ]]; then
            echo -e "${LRED}[FAIL]${NC} Testcase $batch_num-$testcase_num failed."
            if [[ $rc -eq 2 ]]; then
                mv "$WDIR/$TLOG" "$LOGDIR/p1-$batch_num-$testcase_num-error.log"
                echo -e "${LPURPLE}[FATAL]${NC} Unexpected error occured in '$TENTRY'. Please check '$LOGDIR/p1-$batch_num-$testcase_num-error.log'."
            fi
            batch_failed=1
            failed_tests+=(${testcase_num})
        else
            echo -e "${LGREEN}[PASS]${NC} Testcase $batch_num-$testcase_num passed."
            final_score=$(add "$final_score" "$cur_score")
            final_score_per_batch=$(add "$final_score_per_batch" "$cur_score")
        fi

        rm -rf "$WDIR"
    done

    echo -e "\n${LCYAN}--------------------- Batch $batch_num report ----------------------${NC}\n"
    echo -e "${GREEN}Score${NC}: $final_score_per_batch/$total_score_per_batch"
    if [ ${#failed_tests[@]} -ne 0 ]; then
        echo -e "${RED}Failed testcase(s)${NC}: ${failed_tests[*]}"
    else
        echo -e "All testcases passed."
    fi

    if [[ $batch_failed -ne 0 ]]; then
        echo -e "\n${LPURPLE}Final Score${NC}: $final_score/$total_score"
        exit 0;
    fi
    # if [[ $batch_failed -ne 0 ]]; then break; fi
done

# P1DIR="[CORRECT P1 IMPLEMENTATION]"

echo -e "\n${LGREEN}=================== Testcases for part2 ====================${NC}"

for batch_path in "${PART2_BATCHES[@]}"; do
    batch_num="$(basename "$batch_path")"

    echo -e "\n${LYELLOW}=================== Processing batch $batch_num ====================${NC}"

    TESTCASES=("$batch_path"/*)
    batch_failed=0
    total_score_per_batch=0
    final_score_per_batch=0
    failed_tests=()

    for testcase_path in "${TESTCASES[@]}"; do

        if [[ -f "$testcase_path/points" ]]; then
            cur_score=$(cat "$testcase_path/points")
        else
            cur_score=0
        fi

        total_score_per_batch=$(add "$total_score_per_batch" "$cur_score")
        testcase_num="$(basename "$testcase_path")"

        echo -e "\n${LBLUE}------------------ Running testcase $batch_num-$testcase_num ------------------${NC}\n"

        if [[ -f "$testcase_path/description" ]]; then
            echo -e "${LWHITE}-------------- Description for testcase ${batch_num}-${testcase_num} --------------${NC}\n"
            cat "$testcase_path/description"
            echo ""
        fi


        echo -e "${LWHITE}---------------------- Script output -----------------------${NC}\n"

        cp -r "$WTDIR" "$WDIR"
        cp -r "$testcase_path" "$WDIR/testcase"
        mv "$WDIR/testcase/$TENTRY" "$WDIR/$TENTRY" > /dev/null 2>&1
        cp -r "$P1DIR" "$WDIR/part1"
        cp -r "$P2DIR" "$WDIR/part2"
        [[ -d "$WDIR/testcase/src" ]] && cp -i "$WDIR/testcase/src"/* "$WDIR/part2"
        [[ -f "$WDIR/testcase/sha256.patch" ]] && patch "$WDIR/include/hw4/sha256.h" < "$WDIR/testcase/sha256.patch" > /dev/null 2>&1

        run "make P1=part1 P2=part2 > /dev/null 2>&1"
        # run "make P1=part1 P2=part2"
        if [[ $? -ne 0 ]]; then
            echo -e "${LRED}[FAIL]${NC} Compilation error."
            batch_failed=1
            failed_tests+=("$testcase_num")
            rm -rf "$WDIR"
            continue
        fi

        if [[ ! -f "$WDIR/$TENTRY" ]]; then
            echo -e "${LCYAN}[INFO]${NC} '$TENTRY' not found in testcase $batch_num-$testcase_num."
        else
            run "python3 $TENTRY 2>$TLOG"
        fi

        rc="$?"
        if [[ $rc -ne 0 ]]; then
            echo -e "${LRED}[FAIL]${NC} Testcase $batch_num-$testcase_num failed."
            if [[ $rc -eq 2 ]]; then
                mv "$WDIR/$TLOG" "$LOGDIR/p2-$batch_num-$testcase_num-error.log"
                echo -e "${LPURPLE}[FATAL]${NC} Unexpected error occured in '$TENTRY'. Please check '$LOGDIR/p2-$batch_num-$testcase_num-error.log'."
            fi
            batch_failed=1
            failed_tests+=(${testcase_num})
        else
            echo -e "${LGREEN}[PASS]${NC} Testcase $batch_num-$testcase_num passed."
            final_score=$(add "$final_score" "$cur_score")
            final_score_per_batch=$(add "$final_score_per_batch" "$cur_score")
        fi

        rm -rf "$WDIR"
    done

    echo -e "\n${LCYAN}--------------------- Batch $batch_num report ----------------------${NC}\n"
    echo -e "${GREEN}Score${NC}: $final_score_per_batch/$total_score_per_batch"
    if [ ${#failed_tests[@]} -ne 0 ]; then
        echo -e "${RED}Failed testcase(s)${NC}: ${failed_tests[*]}"
    else
        echo -e "All testcases passed."
    fi

    # if [[ $batch_failed -ne 0 ]]; then
    #     echo -e "\n${LPURPLE}Final Score${NC}: $final_score/$total_score"
    #     exit 0;
    # fi
    if [[ $batch_failed -ne 0 ]]; then break; fi
done

echo -e "\n${LPURPLE}Final report${NC}: $final_score/$total_score"
