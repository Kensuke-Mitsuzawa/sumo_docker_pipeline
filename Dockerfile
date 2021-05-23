FROM ubuntu:18.04
RUN apt update
RUN apt-get install -y software-properties-common less vim
RUN add-apt-repository -y ppa:sumo/stable
RUN apt update
RUN apt-get install -y sumo sumo-tools sumo-doc

