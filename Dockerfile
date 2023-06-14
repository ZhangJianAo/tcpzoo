FROM python:3.8

RUN apt-get update && apt-get install -y \
    iptables \
    tcpdump \
    net-tools  \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
COPY tcpzoo.py /work

CMD python tcpzoo.py setup && python tcpzoo.py server
