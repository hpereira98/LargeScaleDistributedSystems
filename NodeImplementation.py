import Node


class NodeImplementation(Node):

    def handle_gossip(self, src, identifier, payload):
        pass

    def handle_ihave(self, src, identifier):
        pass

    def handle_ack(self, src, identifier):
        pass

    def handle_ask(self, src, identifier):
        pass

    def handle_periodic(self, src, identifier):
        pass

    def handle_gc(self, src):
        pass
