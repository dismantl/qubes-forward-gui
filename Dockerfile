FROM python:3.10

RUN apt update -y && apt upgrade -y
RUN apt install -y python3 python3-pip python3-venv gcc pkg-config cmake
RUN mkdir /build && python3 -m venv /build/.venv
COPY requirements.txt /build/requirements.txt
RUN /build/.venv/bin/pip install -r /build/requirements.txt
RUN apt install -y dbus libdbus-1-dev libdbus-1-3 libglib2.0-dev libcairo2-dev libgirepository1.0-dev ccache qt6-base-dev libxcb-cursor0
RUN apt install -y patchelf

# RUN apk add --update musl-dev gcc python3-dev py3-pip chrpath git patchelf qt6-qtbase-dev
# RUN mkdir /build && python3 -m venv /build/.venv
# COPY requirements.txt /build/requirements.txt
# RUN export PATH=/usr/lib/qt6/bin:$PATH
# RUN apk add --update g++ make automake py3-qt6 py3-loguru py3-peewee ccache
# RUN PATH=/usr/lib/qt6/bin:$PATH which qmake
# # RUN PATH=/usr/lib/qt6/bin:$PATH /build/.venv/bin/pip install nuitka
# RUN pip3 install nuitka --break-system-packages
# RUN pip3 install pyinstaller --break-system-packages
