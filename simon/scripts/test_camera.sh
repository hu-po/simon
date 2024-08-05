#!/bin/bash

# Define environment variables
VIDEO_DURATION=1000 #ms
IMAGE_WIDTH=768
IMAGE_HEIGHT=768
SAVE_DIRECTORY=/tmp
VIDEO_DEVICE=/dev/video0
IMAGE_FILENAME=test.png
VIDEO_FILENAME=test.mp4

# List devices
v4l2-ctl --list-devices

# Streaming camera (this command doesn't directly map to libcamera, but you can check devices)
echo -e "\n\n\n📷 Streaming camera\n\n\n"
libcamera-vid --fullscreen -t $VIDEO_DURATION --width $IMAGE_WIDTH --height $IMAGE_HEIGHT

# Taking image
echo -e "\n\n\n📷 Taking image $SAVE_DIRECTORY/$IMAGE_FILENAME\n\n\n"
libcamera-still -o "$SAVE_DIRECTORY/$IMAGE_FILENAME" --width $IMAGE_WIDTH --height $IMAGE_HEIGHT

# Recording video
echo -e "\n\n\n📷 Recording video ($VIDEO_DURATION seconds) $SAVE_DIRECTORY/$VIDEO_FILENAME\n\n\n"
libcamera-vid -t $VIDEO_DURATION --width $IMAGE_WIDTH --height $IMAGE_HEIGHT -o "$SAVE_DIRECTORY/$VIDEO_FILENAME"