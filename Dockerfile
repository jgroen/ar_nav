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
	libboost-python-dev \
	cmake \
	install python-pip \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install dlib -y

RUN pip install scikit-image -y

# Apache site configuration
ADD chute/000-default.conf /etc/apache2/sites-available/

#  Get the web frontend
ADD chute/web /var/www/html

# Install files required by the chute.
#
# ADD <path_inside_repository> <path_inside_container>
#
ADD chute/ar_nav.py /usr/local/bin/ar_nav.py
ADD chute/run.sh /usr/local/bin/run.sh

# Set the work dir for nodejs photo server
WORKDIR "/var/www/html"

EXPOSE 80 81 8010

CMD ["/bin/bash", "/usr/local/bin/run.sh"]
