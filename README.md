# Augmented Reality Navigation for Paradrop

ar_navigation Chute

## Catagory: Augmented Reality, Navigation, Computer Vision

Requirements:
* Wireless security cam that can connect to the Paradrop router.

## Description:

An Augmented Reality Navigation system using computer vision to recognize specific checkpoints along a pre-determined route.    All images are kept within the router without getting sent to the cloud.  Eventually, the route will be cacluated in the cloud using grap methods and machine learning- for now the route is predetermined.
* Configure JSON with ports "8888":"8888"
* Configure the webcam to connect to the SSID and dhcp, disable authentication for images.

##Files

* Dockerfile: Uses apache2, nodejs, python-imaging, iptables, libboost-python-dev cmake, python-dlib, python-scikit-image
* ar\_nav.py: Takes in one arguments for time scale. According to this parameter, takes in an image and looks for a CP.  If the CP is found, it returns the image with the checkpoint highlighted.
* run.sh


