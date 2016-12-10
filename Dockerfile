# Augmented Reality Navigation (ar_nav) v 1

# Version 1.0.0
FROM paradrop/workshop

# Install dependencies.  You can add additional packages here following the example.
RUN apt-get -y update
RUN apt-get install -y --fix-missing \
#	<package> \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-dev \
    libavcodec-dev \
    libavformat-dev \
    libboost-all-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python-dev \
    python-numpy \
    python-protobuf\
    software-properties-common \
    zip \
    iptables \
    python-pillow \
    python-skimage \
    python-pip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN git clone https://github.com/davisking/dlib.git && \
    cd /dlib/examples && \
    mkdir build && \
    cd build  && \
    cmake .. && \
    cmake --build .

RUN cd ~ && \
    cd dlib && \
    python setup.py

# ADD <path_inside_repository> <path_inside_container>
ADD chute/TestServer_v10.py /usr/local/bin/TestServer_v10.py
ADD chute/run.sh /usr/local/bin/run.sh
ADD chute/cp1.svm /usr/local/bin/cp1.svm
ADD chute/cp2.svm /usr/local/bin/cp2.svm
ADD chute/cp3.svm /usr/local/bin/cp3.svm

EXPOSE 8888

CMD ["/bin/bash", "/usr/local/bin/run.sh"]
