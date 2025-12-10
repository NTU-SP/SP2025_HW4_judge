#!/bin/bash

CE="docker"

LRED='\033[1;31m'
LWHITE='\033[1;37m'
NC='\033[0m'

echo -e -n "${LWHITE}[ASK]${NC} Configure your container engine ? [Default: docker] "
read ce
if [[ -n "$ce" ]]; then CE="$ce"; fi

echo -e "${LCYAN}[INFO]${NC} Your container engine is set to '$CE'."
$CE -v > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo -e "\n${LRED}[ERR]${NC} \`$CE -v\` returns an error."
    exit 1
fi

cd "$(dirname $0)" && $CE build -t sp_hw4 .
