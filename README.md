# Augmented Reality Navigation for Paradrop

ar_navigation Chute

## Catagory: Augmented Reality, Navigation, Computer Vision

Requirements:
* Wireless security cam that can connect to the Paradrop router.

## Description:

An Augmented Reality Navigation system using computer vision to recognize specific checkpoints along a pre-determined route.    All images are kept within the router without getting sent to the cloud.  Eventually, the route will be cacluated in the cloud using grap methods and machine learning- for now the route is predetermined.
* Configure JSON with ports "80":"5000","81":"81","8010":"8010"
* Configure the webcam to connect to the SSID and dhcp, disable authentication for images.

##Files

* Dockerfile: Uses apache2, nodejs, python-imaging, iptables, libboost-python-dev cmake, python-dlib, python-scikit-image
* ar\_nav.py: Takes in one arguments for time scale. According to this parameter, takes in an image and looks for a CP.  If the CP is found, it returns the image with the checkpoint highlighted.
* run.sh

## Getting Started

1. Fork this project to your own github account.
2. ar\_nav.py is the main file where the functionality of motion detection lies. [httplib](https://docs.python.org/2/library/httplib.html) is used for getting the file handle.
3. Change the run.sh for tweaking the parameters.

When creating a version of this chute, you should configure it as
shown in the image.  Your camera will be pre-configured to connect to a
certain ESSID, which you should enter in the form.  You will be given
this information during the workshop.  Also, be sure to add the three
port bindings as shown.

![Create version options](/images/create_version.png)

