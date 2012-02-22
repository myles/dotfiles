#!/bin/bash

APP_STORE_APPS=`find /Applications -path '*Contents/_MASReceipt/receipt' \
  -maxdepth 3 -print | sed 's#.app/Contents/_MASReceipt/receipt#.app#g'`

echo $APP_STORE_APPS
