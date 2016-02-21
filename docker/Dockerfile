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

RUN pip uninstall pyparsing -y; exit 0
RUN pip install markdown scss jinja2 pyparsing==1.5.7

# SSHd server (only exposed to other containers)
RUN apt-get install -y openssh-server
RUN mkdir /var/run/sshd
#RUN useradd jenkins
#RUN echo 'jenkins:pass' | chpasswd

RUN echo 'root:pass' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Enable something for jenkins to be able to connect
RUN echo 'KexAlgorithms curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1,diffie-hellman-group1-sha1' >> /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
