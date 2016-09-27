#!/usr/bin/env bash


cd "$(dirname "${BASH_SOURCE[0]}")"


python -c "from Patent.runner import write_database_to_excel; write_database_to_excel();"