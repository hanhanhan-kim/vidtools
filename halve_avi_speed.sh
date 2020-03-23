# Can't convert mjpg to a frame rate greather than about 65 Hz. 
# Videos captured at faster frame rates need to be converted to a slower rate,
# then converted to a faster rate afterwards. 
# This script speeds or slow down compressed avis by a desired factor. 

# See https://askubuntu.com/questions/754316/how-can-the-speed-of-an-avi-file-be-changed as reference

ffmpeg -i *_converted.avi \
       -filter:v "setpts=0.5*PTS" \
       -c:v mpeg4 -q:v 1 \
       -an \
       movie_converted_full_speed.avi