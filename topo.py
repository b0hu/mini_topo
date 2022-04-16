from mininet.topo import Topo

class MyTopo(Topo):

    def __init__(self):

        "Create custom topology"
        Topo.__init__(self)

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        self.addLink(s1,h1,bw=100)
        self.addLink(s1,h2,bw=100)
        self.addLink(s1,s2,bw=1000,loss = 5)
        self.addLink(s2,h3,bw=100)
        self.addLink(s2,s3,bw=1000,loss = 5)
        self.addLink(s3,h4,bw=100)
        self.addLink(s3,s4,bw=1000,loss = 5)
        self.addLink(s3,h4,bw=100)
        self.addLink(s4,h5,bw=1000,loss = 5)
        self.addLink(s4,h6,bw=1000,loss = 5)

topos = {'mytopo': (lambda : MyTopo() )}