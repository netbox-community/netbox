#!/bin/bash

# Exit code starts at 0 but is modified if any checks fail
EXIT=0

# Output a line prefixed with a timestamp
info()
{
	echo "$(date +'%F %T') |"
}

# Track number of seconds required to run script
START=$(date +%s)
echo "$(info) starting build checks."

# Syntax check all python source files
SYNTAX=$(find . -name "*.py" -type f -exec python -m py_compile {} \; 2>&1)
if [[ ! -z $SYNTAX ]]; then
	echo -e "$SYNTAX"
	echo -e "\n$(info) detected one or more syntax errors, failing build."
	EXIT=1
fi

# Show build duration
END=$(date +%s)
echo "$(info) exiting with code $EXIT after $(($END - $START)) seconds."

exit $EXIT
