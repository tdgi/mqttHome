import sys
import time
import pjsua2 as pj
import logging
from multiprocessing import Process, get_context

""" Subclass to extend the pjsua2 Account """
class Account(pj.Account):
    def onRegState(self, prm):
        print("***OnRegState: " + prm.reason)
        
class CallHandle(pj.Call):
    
    media_index = -1
    video_index = -1
    call_active = False
    
    def __init__(self, acc, call_id = pj.PJSUA_INVALID_ID):
        pj.Call.__init__(self, acc, call_id)
        
    def onCallState(self, prm):
        ci = self.getInfo()
        if hasattr(self, "last_state"):
            self.last_state.value = ci.stateText.encode()
        if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            self.call_active = False
            self.call_duration.value = ci.connectDuration.sec
            self.total_duration.value = ci.totalDuration.sec
            self.remote_uri.value = ci.remoteUri.encode()
        if ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
            self.call_active = True
            
        return pj.Call.onCallState(self, prm)
                       
    def onCallMediaState(self, prm):
        ci = self.getInfo()
        for mi in ci.media:
            if mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE and mi.type == pj.PJMEDIA_TYPE_AUDIO:
                self.media_index = mi.index
                self.codec_name.value = self.getStreamInfo(mi.index).codecName.encode()
                self.remote_rtp.value = self.getStreamInfo(mi.index).remoteRtpAddress.encode()
                self.video_protocol.value = self.getStreamInfo(mi.index).proto
            if mi.status != pj.PJSUA_CALL_MEDIA_NONE and mi.type == pj.PJMEDIA_TYPE_VIDEO:
                self.video_index = mi.index
                self.video_codec.value = self.getStreamInfo(mi.index).codecName.encode()
                self.video_rtp.value = self.getStreamInfo(mi.index).remoteRtpAddress.encode()

        return pj.Call.onCallMediaState(self, prm)
                
    def onStreamDestroyed(self, prm):
        self.tone_player = None 
        self.player = None
        self.recorder = None
        logger.info(self.dump(True, ""))
        return pj.Call.onStreamDestroyed(self, prm)
    
    def onDtmfDigit(self, prm):
        logger.info("Received DTMF: {}".format(prm.digit))
        self.dtmf_string.value += prm.digit.encode()
        return pj.Call.onDtmfDigit(self, prm)
    
    def onCallTsxState(self, prm):
        if prm.e.body.tsxState.type == pj.PJSIP_EVENT_RX_MSG and prm.e.body.tsxState.src.rdata.info.startswith("Request msg INFO"):
            for line in prm.e.body.tsxState.src.rdata.wholeMsg.splitlines():
                if line.startswith("Signal="):
                    sig = line.split("=")[1]
                    logger.info("Received SIP INFO signal: {}".format(sig))
                    self.sipinfo_string.value += sig.encode()
    
        return pj.Call.onCallTsxState(self, prm)
    
"""
class SIP(get_context("fork").Process):
    def __init__(self, proc_name="sip_caller"):
        super(SIP, self).__init__(name=proc_name, daemon=True)
        self.start()
    
    def __enter__(self):
        pass
    
    def __exit__(self, exc_type, exc_value, tracebackf):
        pass
        
    def run(self):
        self.start_caller()
            
    def start_caller(self):
        ep_cfg = pj.EpConfig()
        self.ep = pj.Endpoint()
        self.ep.libCreate()
        self.ep.libInit(ep_cfg)
        
        sipTpConfig = pj.TransportConfig()
        sipTpConfig.port = 5060
        self.ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, sipTpConfig)
        self.ep.libStart()
        
        acfg = pj.AccountConfig()
        acfg.idUri = "sip:101@192.168.2.5:5060;transport=udp"
        acfg.regConfig.registrarUri = "sip:192.168.2.5:5060;transport=udp"
        cred = pj.AuthCredInfo("digest", "*", "101", 0, "101")
        acfg.sipConfig.authCreds.append(cred)
        
        self.acc = Account()
        self.acc.create(acfg)
        time.sleep(5)    
        self.ep.libDestroy()
        # time.sleep(5)
        print("\nRegistered !")
"""
    
# def init_call(uri):
#     c = CallHandle(self.account)
#     call_prm = pj.CallOpParam()
#     call_prm.opt.audioCount = 1
#     call_prm.opt.videoCount = 0
#     call_prm.opt.flag = pj.PJSUA_CALL_INCLUDE_DISABLED_MEDIA
#     c.makeCall("{};transport=udp".format(uri), call_prm) # self.transport_string = ";transport=udp"        
    
def toCall():
    # Init the library
    ep_cfg = pj.EpConfig()
    ep = pj.Endpoint()
    ep.libCreate()
    ep.libInit(ep_cfg)
    
    # Create SIP transport
    sipTpConfig = pj.TransportConfig();
    sipTpConfig.port = 5060;
    ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, sipTpConfig)
    ep.libStart()
    
    acfg = pj.AccountConfig()
    acfg.idUri = "sip:100@192.168.2.5:5060;transport=udp"
    acfg.regConfig.registrarUri = "sip:192.168.2.5:5060;transport=udp"
    cred = pj.AuthCredInfo("digest", "*", "100", 0, "100")
    acfg.sipConfig.authCreds.append(cred)
    
    # Create the account
    acc = Account()
    acc.create(acfg)
    # time.sleep(10)
    
    c = CallHandle(acc)
    call_prm = pj.CallOpParam()
    call_prm.opt.audioCount = 1
    call_prm.opt.videoCount = 0
    #call_prm.opt.flag = pj.PJSUA_CALL_INCLUDE_DISABLED_MEDIA
    
    c.makeCall("sip:101@192.168.2.5;transport=udp", call_prm)
    time.sleep(3)
    ep.hangupAllCalls()
    ep.libDestroy()
        
if __name__ == "__main__":
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    hdlr = logging.StreamHandler(sys.stdout)
    logger.addHandler(hdlr)

    toCall()
        