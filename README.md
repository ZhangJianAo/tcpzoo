# TcpZoo

TcpZoo is a utility that allows you to simulate various TCP errors for testing and validation purposes.

## Usage

1. Start the container
   ```
   docker run --rm -it --name tcpzoo --cap-add NET_ADMIN tcpzoo:latest
   ```

   After the container starts, it will output the ports it is listening on.

2. Login into the container and run the test
   ```
   docker exec -it tcpzoo bash
   ```

   After logging in, run the test with the command:
   ```
   python tcpzoo.py request
   ```

   This command will run curl on every port on which the server is listening.

   Except for the 8000 port, other ports will generate tcp errors. You can see the curl message for each port.

If you want to test your own program, mount it in the container using the ```--volume or -v``` in the docker run command, or run your program in another container and access servers via the docker internal network.

**DO NOT publish ports to the host using ```--publish or -p```, as the tcp error will be masked by port publishing.**

## Details

The utility is written in Python, in the tcpzoo.py file.

Some TCP errors are created by iptables rules, others are created by the program.

```python tcpzoo.py setup``` sets iptables rules. This is why I've placed this utility in Docker, although theoretically, this tool can also run in a Linux box with iptables installed.

```python tcpzoo.py clean``` cleans iptable rules that were set up by this script.

```python tcpzoo.py server``` starts a web server to listen on every port.

So when the container starts, the following command will be run: ```python tcpzoo.py setup && python tcpzoo.py server```.

```python tcpzoo.py request``` starts a curl request to query every port for testing.

## TCP Errors

The following list shows every port and its corresponding TCP errors:

* 8000: No errors, just a normal web server returning some text.
* 8001: SYN packet will be dropped.
* 8002: ACK packet will be dropped.
* 8003: Connection rejected with ICMP Destination Unreachable Message.
* 8004: Connection rejected with RST packet.
* 8005: Server sends ICMP Destination Unreachable Message to reject connection after three-way handshake.
* 8006: Server sends RST packet after three-way handshake.
* 8007: Server closes connection after receiving HTTP request.
* 8008: Server sends RST packet after receiving HTTP request.
