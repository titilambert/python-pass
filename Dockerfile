FROM debian:testing

# Click needs this for python3 support
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt-get update
RUN apt-get install -y vim git python-pip tree gnupg2 python3 pypy
RUN pip install tox

RUN git config --global user.email "you@example.com"
RUN git config --global user.name "Your Name"

ADD pypass pypass/pypass
ADD docs pypass/docs
ADD setup.py pypass/setup.py
ADD setup.cfg pypass/setup.cfg
ADD requirements.txt pypass/requirements.txt
ADD test-requirements.txt pypass/test-requirements.txt
ADD docs-requirements.txt pypass/docs-requirements.txt
ADD README.rst pypass/README.rst
ADD tox.ini pypass/tox.ini
ADD .git pypass/.git

# Install testing gpg key
RUN gpg --allow-secret-key-import --import pypass/pypass/tests/test_key_sec.asc
RUN gpg --import-ownertrust pypass/pypass/tests/test_ownertrust.txt

RUN pip install -r pypass/requirements.txt
RUN cd pypass && python setup.py install

