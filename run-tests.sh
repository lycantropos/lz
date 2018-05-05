#!/usr/bin/env bash

set -e

docker-compose up --build --exit-code-from lz

STATUS=$?

docker-compose down --remove-orphans

if [ "$STATUS" -eq "0" ]; then
	echo "Tests passed";
else
	echo "Tests failed to pass"
fi

exit ${STATUS}
