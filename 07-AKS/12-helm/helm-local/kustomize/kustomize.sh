#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cat <&0 >${SCRIPT_DIR}/all.yaml
kustomize build ${SCRIPT_DIR} && rm ${SCRIPT_DIR}/all.yaml