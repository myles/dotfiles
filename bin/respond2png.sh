#!/bin/bash

webkit2png --scale=1 --width 320 -o "iPhone-Portrait" $1
webkit2png --scale=1 --zoom 2 --width 320 -o "iPhone-Portrait@2x" $1

webkit2png --scale=1 --width 568 -o "iPhone-Landscape" $1
webkit2png --scale=1 --zoom 2 --width 568 -o "iPhone-Landscape@2x" $1

webkit2png --scale=1 --width 768 -o "iPad-Portrait" $1
webkit2png --scale=1 --zoom 2 --width 768 -o "iPad-Portrait@2x" $1

webkit2png --scale=1 --width 1024 -o "iPad-Landscape" $1
webkit2png --scale=1 --zoom 2 --width 1024 -o "iPad-Landscape@2x" $1
