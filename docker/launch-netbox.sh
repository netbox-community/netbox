#!/bin/bash

UNIT_CONFIG="${UNIT_CONFIG-/etc/unit/nginx-unit.json}"
UNIT_SOCKET="/opt/unit/unit.sock"

load_configuration() {
  MAX_WAIT=10
  WAIT_COUNT=0
  while [ ! -S $UNIT_SOCKET ]; do
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
      echo "⚠️ No control socket found; configuration will not be loaded."
      return 1
    fi

    WAIT_COUNT=$((WAIT_COUNT + 1))
    echo "⏳ Waiting for control socket to be created... (${WAIT_COUNT}/${MAX_WAIT})"

    sleep 1
  done

  # even when the control socket exists, it does not mean unit has finished initialisation
  # this curl call will get a reply once unit is fully launched
  curl --silent --output /dev/null --request GET --unix-socket $UNIT_SOCKET http://localhost/

  echo "⚙️ Applying configuration from $UNIT_CONFIG"

  RESP_CODE=$(
    curl \
      --silent \
      --output /dev/null \
      --write-out '%{http_code}' \
      --request PUT \
      --data-binary "@${UNIT_CONFIG}" \
      --unix-socket $UNIT_SOCKET \
      http://localhost/config
  )
  if [ "$RESP_CODE" != "200" ]; then
    echo "⚠️ Could no load Unit configuration"
    kill "$(cat /opt/unit/unit.pid)"
    return 1
  fi

  echo "✅ Unit configuration loaded successfully"
}

load_configuration &

exec unitd \
  --no-daemon \
  --control unix:$UNIT_SOCKET \
  --pid /opt/unit/unit.pid \
  --log /dev/stdout \
  --state /opt/unit/state/ \
  --tmp /opt/unit/tmp/
