FROM ubuntu:16.04

# Update default packages
RUN apt-get update

# Get Ubuntu packages
RUN apt-get install -y \
    build-essential \
    curl
    
# Update new packages
RUN apt-get update

# Get Rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc

# Python
WORKDIR /opt/app
COPY .src/requirements.txt requirements.txt

RUN set -xe \
    && apt-get update \
    && apt-get install python-pip
RUN pip install --upgrade pip

RUN  pip install  --no-cache-dir -r requirements.txt
COPY . .

# how to run gunicorn on docker
# https://stackoverflow.com/questions/43925487/how-to-run-gunicorn-on-docker
CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "main:app"]