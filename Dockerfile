# Augmented Reality Navigation (ar_nav) v 1

# Version 1.0.0
FROM ubuntu:14.04

# Install dependencies.  You can add additional packages here following the example.
RUN apt-get update && apt-get install -y \
#	<package> \
	build-essential \
	cmake \
	curl \
	git \
	iptables \
	nodejs \
	python-imaging \
	python-matplotlib \
	python-numpy \
	python-pillow \
	python-scipy \
	build-essential \
	cython \
	libboost-all-dev \
	libjpeg-dev \
	pkg-config \
	python-dev \
	zip \
	python-pip \
	python-skimage \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

RUN cd ~ && \
    mkdir -p dlib-tmp && \
    cd dlib-tmp && \
    curl -L \
         https://github.com/davisking/dlib/archive/v19.0.tar.gz \
         -o dlib.tar.bz2 && \
    tar xf dlib.tar.bz2 && \
    cd dlib-19.0/python_examples && \
    mkdir build && \
    cd build && \
    cmake ../../tools/python && \
    cmake --build . --config Release && \
    cp dlib.so /usr/local/lib/python2.7/dist-packages && \
    rm -rf ~/dlib-tmp
# Install files required by the chute.

# ADD <path_inside_repository> <path_inside_container>
ADD chute/TestServer_v6.py /usr/local/bin/TestServer_v6.py
ADD chute/run.sh /usr/local/bin/run.sh
ADD chute/cp1.svm /usr/local/bin/cp1.svm
ADD chute/cp2.svm /usr/local/bin/cp2.svm
ADD chute/cp3.svm /usr/local/bin/cp3.svm

EXPOSE 8888

CMD ["/bin/bash", "/usr/local/bin/run.sh"]
