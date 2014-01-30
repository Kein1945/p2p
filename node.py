from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import threading
import jsonrpclib
import hashlib
import random
import socket
import time


DEFAULT_PORT = 8335

hashname = hashlib.sha256

class Node(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self._server = None
		self._stop_server = False
		self._start = -1
		try:
			server = self._get_server()
			server.register_function(lambda x: x, 'ping')
			server.register_function(self.stop, 'stop')
			server.register_instance(self)
		except socket.error:
			self._server = None
		self.providers = [Peer_Provider()]

		self._idx = hashname( str(random.random()) ).hexdigest()

	def run(self):
		self.listen()

	def listen(self):
		if self._server is None:
			return True
		server = self._get_server()
		print "Start listen"
		self._start = time.time()
		while not self._stop_server:
			server.handle_request()


	def stop(self):
		print "Server is shutting down.."
		self._stop_server = True
		return True

	def uptime(self):
		return time.time() - self._start

	def _get_server(self, host='localhost', port=DEFAULT_PORT):
		if self._server is None:
			print "Creating new server %s:%s" % (host,port)
			self._server = SimpleJSONRPCServer((host,port))
		return self._server

	def find_peers(self):
		self.peers = []
		for provider in self.providers:
			for peer_addr in provider.get_peers():
				peer = Peer(peer_addr)
				if peer.is_alive():
					self.peers.append(peer)
		return self.peers

	def whoareyou(self):
		return self._idx

	def _dispatch(self, *args):
		print [self, args]
		try:
			method = getattr(self, args[0])
			return method(*args[1])
		except AttributeError:
			return [args, "Unknown command"]


class Peer:

	def __init__(self, peer_addr):
		self.rpc = jsonrpclib.Server('http://%s:%d' % peer_addr)
		self.idx = self.rpc.whoareyou()

	def is_alive(self):
		key = 7
		return key == self.rpc.ping(key)

	def __str__(self):
		return self.idx[:8]


class Peer_Provider:

	def get_peers(self):
		return [('localhost', DEFAULT_PORT)]

def main():
	node = Node()
	node.start()
	nodes = node.find_peers()
	print "Peers:"
	for peer in nodes:
		print "%s\tuptime\t%d" % (peer, peer.rpc.uptime())
		# peer.stop()


if __name__ == '__main__':
	main()