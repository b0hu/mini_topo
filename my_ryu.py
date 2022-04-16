from operator import attrgetter

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub


class SimpleMonitor13(simple_switch_13.SimpleSwitch13):
    super(SimpleMonitor13, self).__init__(*args, **kwargs)
    self.datapaths = {}
    self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(5)
    
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body
        
        self.logger.info('***************************')

        self.logger.info('Switch ID: %x',ev.msg.datapath.id)
        self.logger.info('Port No '
                        'Tx-Bytes '
                        'Rx-Bytes ')
        self.logger.info('-------- '
                        '--------- '
                        '---------')
        for info in sorted(stat, key=attrgetter('port_no'):
            self.logger.info('%8x %8d %8d',
                            stat.port_no,
                            stat.rx_bytes,
                            stat.tx_bytes)
    
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('MAC Address Table    Port No.')
        self.logger.info('-----------------------------')

        for stat in sorted([flow for flow in body if flow.priority == 1],
                        key=lambda flow: (flow.match['in_port'],
                                            flow.match['eth_dst'])):
            self.logger.info('%s %7d',
                            stat.match['eth_dst'],
                            stat.instructions[0].actions[0].port)
        
        self.logger.info('***************************')
