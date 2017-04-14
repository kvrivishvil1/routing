# Routing

In this project, I am implementing distance-vector routing, a distributed routing algorithm where multiple routers cooperate to transport packets to their destinations efficiently. The routing algorithm will run on each router within a simulated network. Each router will exchange messages with neighboring routers and hosts to construct a forwarding table. As the network topology changes, the routing algorithm will update the forwarding tables to maintain connectivity.

## Learning Switch

I have implemented a learning switch in `learning_switch.py`. A learning switch is not a very effective routing technique; its greatest shortcoming is that it breaks when the network has loops.

That is why DV Router is more powerful.

## Distance-Vector Router

## Installation and Running the Project

The network simulator models network entities and the links between them as Python objects.

To run the DV Router, do:

	python simulator.py --default-switch-type=dv_router topos.linear

### Netvis
NetVis is a visualization and interactivity tool for the network
simulator. It is written using Processing, which is basically a
framework for writing visualization tools in Java (with some nice
shortcuts). Here's how to get NetVis running:

1.  [Download Processing](https://processing.org/download/?processing) for your
    platform, install it, and run it.

2.  Install the [ControlP5](https://github.com/sojamo/controlp5) library from
    within Processing: go to Sketch → Import Library... → Add Library..., search
    for ControlP5, and click Install.

3.  If you don't have the the JDK, install it.

4.  Compile the `json` library included with NetVis by running
    `netvis/code/json/src/build.sh` and answer the prompt.

5.  In Processing, go to File → Open..., and open up `netvis/NetVis.pde`.

6.  Start `simulator.py` from the command line as described above.

7.  In Processing, press the play button to run NetVis. You should see a purple
    window with your topology!



