FROM debian:12

RUN apt update -y && apt upgrade -y
RUN apt install -y python3 python3-pip python3-venv gcc pkg-config cmake
RUN mkdir /build && python3 -m venv /build/.venv
COPY requirements.txt /build/requirements.txt
RUN /build/.venv/bin/pip install -r /build/requirements.txt
RUN apt install -y dbus libdbus-1-dev libdbus-1-3 libglib2.0-dev libcairo2-dev libgirepository1.0-dev qt6-base-dev libxcb-cursor0