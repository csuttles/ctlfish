import argparse
import sys
import socket

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', type=str, metavar='host', default=None, help='IP addr of host')
parser.add_argument('-p', '--port', type=int, metavar='port', default=80, help='TCP port')
args = parser.parse_args()

print(f"Connecting to: {args.host}:{args.port}")

# create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:

    # connect using the socket object instance
    client.connect((args.host, args.port))

    # send some data
    send_bytes = b'GET / HTTP/1.0\r\n\r\n'
    print(f'sending:\n{send_bytes.decode("utf-8")}')
    client.send(send_bytes)

    # recv some the response
    response = client.recv(4096)

# when we exit the context manager we implicitly clean up the socket
print(response.decode('utf-8'))

# exit 0 to indicate success
sys.exit(0)
