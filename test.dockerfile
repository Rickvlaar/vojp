FROM ubuntu:latest

WORKDIR ~

# Without interactive dialogue
ARG DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update
RUN apt-get install -y wget gnupg2 software-properties-common git apt-utils vim dirmngr apt-transport-https ca-certificates

# Installing NVM, NodeJS and NPM
RUN wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.2/install.sh | bash
ENV NODE_VERSION=11
RUN . $HOME/.nvm/nvm.sh && nvm install $NODE_VERSION && nvm alias default $NODE_VERSION && nvm use default

# Install Wine from WineHQ Repository
RUN dpkg --add-architecture i386
RUN wget -qO- https://dl.winehq.org/wine-builds/Release.key | apt-key add -
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv F987672F
RUN apt-add-repository 'deb https://dl.winehq.org/wine-builds/ubuntu/ bionic main'
RUN apt-get update
RUN apt-get install -y --install-recommends winehq-stable

# Installing mono
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
RUN sh -c 'echo "deb https://download.mono-project.com/repo/ubuntu stable-bionic main" > /etc/apt/sources.list.d/mono-official-stable.list'
RUN apt-get update
RUN apt-get install -y mono-complete

RUN PROJECT_DIR=/root/project

WORKDIR $PROJECT_DIR