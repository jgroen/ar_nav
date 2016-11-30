# Augmented Reality Navigation (ar_nav) v 1
#  - Finds ip address webcam - used for detecting motion
# Version 1.0.0
FROM paradrop/workshop
MAINTAINER Paradrop Team <info@paradrop.io>

# Install dependencies.  You can add additional packages here following the example.
RUN apt-get update && apt-get install -y \
#	<package> \
	apache2 \
	iptables \
	nodejs \
	python-imaging \
	python-matplotlib \
	python-numpy \
	python-pillow \
	python-scipy \
	build-essential \
	cython \
	libboost-python-dev \
	cmake \
	python-pip \
	python-skimage \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install dlib

# Install files required by the chute.
#
# ADD <path_inside_repository> <path_inside_container>
#
ADD chute/TestServer_v2.py /usr/local/bin/TestServer_v2.py
ADD chute/run.sh /usr/local/bin/run.sh


EXPOSE 8888

CMD ["/bin/bash", "/usr/local/bin/run.sh"]
