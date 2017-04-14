"""Your awesome Distance Vector router for CS 168."""

import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16

HOST = 0
ROUTER = 1

class DVRouter(basics.DVRouterBase):
    # NO_LOG = True # Set to True on an instance to disable its logging
    POISON_MODE = True # Can override POISON_MODE here
    # DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

    class RoutingTableEntry():
        def __init__(self, port, entity_type, latency):
            self.port = port
            self.entity_type = entity_type
            self.latency = latency
            self.last_updated = api.current_time()

    def __init__(self):
        """
        Called when the instance is initialized.

        You probably want to do some additional initialization here.

        """
        # "destination: RoutingTableEntry()"
        self.routingTable = {}
        # mapping of (port, latency)
        self.linkLatencies = {}
        self.start_timer()  # Starts calling handle_timer() at correct rate

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """
        # send all routes to new neighbors here to let them know we exist
        # send routingPacket to PORT; then handle_rx will be called to handle HostPacket from hosts
        # we learn about what ports are available after this call
        self.linkLatencies[port] = latency
        #  sending all your routes to the new neighbor directly in handle_link_up
        for destination in self.routingTable:
            self.send(basics.RoutePacket(destination, self.routingTable[destination].latency), 
                      port=port, 
                      flood=False)

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.

        """
        if port in self.linkLatencies.keys():
            self.linkLatencies[port] = INFINITY
        # modify all paths that use affected node
        for destination in self.routingTable.keys():
            if self.routingTable[destination].port == port:
                self.send_poison(destination)
                del self.routingTable[destination]
                  
    def update_table(self, destination, port, entity_type, latency):
        self.routingTable[destination] = self.RoutingTableEntry(port, entity_type, latency)
        self.send(basics.RoutePacket(destination, latency), port=port, flood=True)

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        if isinstance(packet, basics.RoutePacket):
            destination = packet.destination
            new_latency = packet.latency + self.linkLatencies[port]

            if destination not in self.routingTable.keys():
                self.update_table(destination, port, ROUTER, new_latency)
                return

            rt_entry = self.routingTable[destination]
            old_latency = rt_entry.latency
 
            if old_latency > new_latency:
                self.update_table(destination, port, ROUTER, new_latency)
                return
            
            if port == rt_entry.port:
                if new_latency >= INFINITY and self.POISON_MODE:
                    self.send_poison(destination)
                    del self.routingTable[destination]
                else:
                    # only refreshes timer; don't send -- split horizon
                    rt_entry.last_updated = api.current_time()

        elif isinstance(packet, basics.HostDiscoveryPacket):
            latency = self.linkLatencies[port]
            self.update_table(packet.src, port, HOST, latency)
        else:
            # drop unseen destination
            if packet.dst not in self.routingTable.keys():
                return
            
            rt_entry = self.routingTable[packet.dst]
            if rt_entry.latency >= INFINITY:
                return
            else:
                bestPort = rt_entry.port
                if bestPort != port:
                    self.send(packet, port=bestPort, flood=False)

    def has_expired(self, last_updated):
        return api.current_time() - last_updated > self.ROUTE_TIMEOUT

    def remove_expired_ports(self):
        for destination in self.routingTable.keys():
            rt_entry = self.routingTable[destination]
            # only keep active "hosts" in router's table for efficient forwarding
            if rt_entry.entity_type == ROUTER and self.has_expired(rt_entry.last_updated):
                self.send_poison(destination)
                del self.routingTable[destination]

    def send_table_to_neighbors(self):
        for destination in self.routingTable.keys():
            latency = self.routingTable[destination].latency
            port = self.routingTable[destination].port
            self.send(basics.RoutePacket(destination, latency), port=port, flood=True)

    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        # expires all ports whose time_now - time_last_updated > 15 seconds
        # send tables to neighbors
        self.remove_expired_ports()
        self.send_table_to_neighbors()

    def send_poison(self, destination):
        if self.POISON_MODE:
            self.send(basics.RoutePacket(destination, INFINITY), flood=True)

