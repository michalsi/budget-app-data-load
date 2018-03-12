#!/usr/bin/env bash

URL=${1:-localhost:8080}
NUMBER_OF_USERS=${2:-1}
DB_NAME=${3:-postgres}
DB_USER=${4:-postgres}
DB_PASSWORD=${5:-mysecretpassword}

python ./data_priming.py --url ${URL} --numberOfUsers ${NUMBER_OF_USERS} --dbname=${DB_NAME} --dbuser=${DB_USER} --dbpassword=${DB_PASSWORD}