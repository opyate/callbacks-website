#!/usr/bin/env bash

curl -X POST http://0.0.0.0:8080/callbacks \
    -u demo: \
    -H 'content-type: application/json'\
    -d @- << EOF
      {
        "url": "http://0.0.0.0:8080/test?payload=<0001f9db>",
        "ts": "1552315623"
      }
EOF
