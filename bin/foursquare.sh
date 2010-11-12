#!/bin/sh
#
# A simple shell script to check into a venue in Foursquare.

CURL=`which curl`
FOURSQUARE_API="http://api.foursquare.com/v1/checkin"

if test -z "$CURL"; then
	echo "curl binary not found"
	exit 1
fi

USERNAME=$1
VENUE_ID=$2

$CURL -v -X POST -u $USERNAME $FOURSQUARE_API --data "vid=$VENUE_ID"
