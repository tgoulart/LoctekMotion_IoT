#!/bin/bash

PORT=/dev/ttyAMA0

echo "hello" > $PORT
cat < $PORT
