#!/bin/bash

S3CMD=/usr/bin/s3cmd
DIRS=('css' 'img' 'js' 'uni_form' 'themes')


if [[ $1 == 'production' ]]
then
  BUCKET_NAME=market-media.greatcoins.com
else
  BUCKET_NAME=market-media.numismatichq.com
fi

for DIR in ${DIRS[*]}
do
  $S3CMD --skip-existing -M -P -r -c s3.cfg sync s3://$BUCKET_NAME/media/$DIR ../media
done
