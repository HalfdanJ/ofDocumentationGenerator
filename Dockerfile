#
#
#
FROM ubuntu:15.10
MAINTAINER Jonas Jongejan "jonas@halfdanj.dk"

RUN apt-get update
RUN apt-get install -y python python-pip wget clang
