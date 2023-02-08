FROM tacc/tacc-ubuntu18-mvapich2.3-ib:latest

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y python3-pip && \
    curl -O https://bootstrap.pypa.io/pip/3.6/get-pip.py && \
    python3 get-pip.py && \
    pip3 install mpi4py numpy==1.19.5 && \
    pip install -U numpy vina

# If ADFR is needed
#RUN curl -0 https://ccsb.scripps.edu/adfr/download/1038/ -o adfr.tar.gz
#RUN tar -xf adfr.tar.gz -d /usr/bin/bash
