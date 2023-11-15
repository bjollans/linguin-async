#!/bin/bash

set -e

pytest

rm -rf ./deployment_dependencies

pip3 install \
    --platform manylinux2014_x86_64 \
    --target=deployment_dependencies \
    --implementation cp \
    --python-version 3.11 \
    --only-binary=:all: --upgrade \
    -r requirements/prod.txt

rm -rf ./lambda_bundle.zip
cd ./deployment_dependencies
zip -r ../lambda_bundle.zip ./*
cd -
rm -rf ./deployment_dependencies
zip lambda_bundle.zip ./* -r -x "lambda_bundle.zip" -x "deployment_dependencies" -x "*__pycache__*"
aws lambda update-function-code --function-name my_lambda --zip-file fileb://lambda_bundle.zip --region eu-central-1
