#!/bin/bash

mkdir temp

# install dependencies locally
pip install -r requirements.txt -t temp

cp -r src temp/

# bundle files for lambda
# As of Build 10.0.26200 of Windows, tar.exe is just broken.
# tar.exe -a -c -f bundle.zip temp     <-- does not work
# use 7z instead
cd temp
7z a -tzip ../bundle.zip *
cd ..

# deploy to aws
aws lambda update-function-code \
    --function-name arxiv_ingest_ondemand \
    --zip-file fileb://bundle.zip \
    --no-cli-page

rm -r temp
rm bundle.zip