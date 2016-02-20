#
#
#
FROM ubuntu:15.10
MAINTAINER Jonas Jongejan "jonas@halfdanj.dk"

RUN apt-get update && apt-get install -y \
python \
python-pip \
clang \
git

RUN apt-get update && apt-get install -y python-levenshtein \
python-clang-3.6  \
libclang-dev=1:3.6-26ubuntu1

RUN git clone -b master https://github.com/openframeworks/openframeworks
#RUN git clone https://github.com/HalfdanJ/ofDocumentationGenerator

RUN pip install markdown scss jinja2

