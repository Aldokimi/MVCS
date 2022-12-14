# MVCS API with SSH Server container
# Base Image

FROM ubuntu:20.04

#Update APT repository && Install OpenSSH
RUN apt-get update \
&& apt-get install -y openssh-server

# Install mysql client and pip
RUN apt-get install -y mysql-client \
&& apt-get install -y default-libmysqlclient-dev \
&& apt-get install -y python3-pip

#Establish the operating directory of OpenSSH
RUN mkdir /var/run/sshd

#Set Root password
RUN echo 'root:hellossh' | chpasswd

#Allow Root login
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' \
    /etc/ssh/sshd_config

#SSH login fix
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional \
    pam_loginuid.so@g' -i /etc/pam.d/sshd

#SSH authorized keys fix
RUN sed '/AuthorizedKeysFile/c\AuthorizedKeysFile     \
    .ssh/authorized_keys .ssh/authorized_keys2/' -i /etc/ssh/sshd_config

#expose port 22
EXPOSE 22

#Commands to be executed by default
CMD ["/usr/sbin/sshd","-D"]

# OS/ARCH linux/ppc64le
#FROM python:3.8 

ENV PYTHONUNBUFFERED 1

# Create the mvcs user which will be the woner of the appliction
RUN useradd mvcs \
&& mkdir /home/mvcs \
&& mkdir /home/mvcs/.ssh \
&& touch /home/mvcs/.ssh/authorized_keys \
&& chmod 700 /home/mvcs/.ssh\
&& chmod 600 /home/mvcs/.ssh/authorized_keys \
&& chown mvcs:mvcs /home/mvcs/.ssh\
&& chown mvcs:mvcs /home/mvcs/.ssh/authorized_keys

# Create the working directory
RUN mkdir /code
WORKDIR /code

# Installing requirements an copying  the data
ADD requirements.txt /code/
RUN pip3 install -r requirements.txt
ADD . /code/
