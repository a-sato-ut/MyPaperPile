#!/bin/bash

set -euo pipefail

CWD=$(dirname $0)

cd $CWD
git pull
git add pdf/*.pdf
git commit -m "update pdf $(date)"
git push
