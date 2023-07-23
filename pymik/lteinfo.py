import ssl
import argparse

from . import librouteros

import mktconfig

from . import timedinput

stdout_template = """Current Operator :{currentoperator}
Access Technology :{accesstechnology}
Primary Band: {primaryband}
CA  Band:{caband}
RSSI: {rssi} ({rssivalue})
RSRP: {rsrp} ({rsrpvalue})
RSRQ: {rsrq} ({rsrqvalue})
SINR: {sinr} ({sinrvalue})"""

html_template = """<div class="table">
    <div class="tr">
        <div class="td left" width="33%">Current Operator</div>
        <div class="td left">{currentoperator}</div>
    </div>
    <div class="tr">
        <div class="td left" width="33%">Access Technology</div>
        <div class="td left">{accesstechnology}</div>
    </div>
    <div class="tr">
        <div class="td left" width="33%">Primary Band</div>
        <div class="td left">{primaryband}</div>
    </div>
    <div class="tr">
        <div class="td left" width="33%">CA Band</div>
        <div class="td left">{caband}</div>
    </div>
    <div class="tr">
        <div class="td left" width="33%">RSSI</div>
        <div class="td left">{rssi} ({rssivalue})</div>
    </div>
    <div class="tr">
        <div class="td left" width="33%">RSRP</div>
        <div class="td left">{rsrp} ({rsrpvalue})</div>
    </div>
    <div class="tr">
        <div class="td left" width="33%">RSRQ</div>
        <div class="td left">{rsrq} ({rsrqvalue})</div>
    </div>
    <div class="tr">
        <div class="td left" width="33%">SINR</div>
        <div class="td left">{sinr} ({sinrvalue})</div>
    </div>
</div>
"""

signal_values = {
    "RSRP":[
        (99999,-80,"Excellent"),
        (-80,-90,"Good"),
        (-90,-100,"Poor"),
        (-100,-99999,"Very Poor")
    ],
    "RSRQ":[
        (99999,-10,"Excellent"),
        (-10,-15,"Good"),
        (-15,-20,"Poor"),
        (-20,-99999,"Very Poor")
    ],
    "SINR":[
        (99999,20,"Excellent"),
        (20,13,"Good"),
        (13,0,"Poor"),
        (0,-99999,"Very Poor")
    ],
    "RSSI":[
        (99999,-65,"Excellent"),
        (-65,-75,"Good"),
        (-75,-85,"Poor"),
        (-85,-99999,"Very Poor")
    ],
}

class ltewatch(object):
    def __init__(self):
        self.api = None
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.set_ciphers('ADH:@SECLEVEL=0')

    def connect(self):
        self.api = librouteros.connect(username=mktconfig.router_user,
            password=mktconfig.router_pw,
            host=mktconfig.router_ip,
            ssl_wrapper=self.ctx.wrap_socket,
            port=mktconfig.router_port)

    def get_api(self):
        if self.api == None:
            self.connect()
        return self.api

    def get_lte_info(self):
        api = self.get_api()
        try:
            lte = api.path('interface','lte')
            g = lte('info',**{'.id':'*1','once':''})
            return tuple(g)
        except librouteros.exceptions.TrapError:
            return None

    def get_word_from_map(self,key,value):
        if value=="" or value==None:
            return ""
        values = signal_values[key]
        for upper,lower,word in values:
            if value<=upper and value>lower:
                return word

    def get_signal_summary(self,lte_info):
        signal_summary = {}
        try:
            rssi = lte_info.get("rssi","")
            rssi = float(rssi)
        except ValueError:
            rssi = ""
        try:
            rsrp = lte_info.get("rsrp","")
            rsrp = float(rsrp)
        except ValueError:
            rsrp = ""
        try:
            rsrq = lte_info.get("rsrq","")
            rsrq = float(rsrq)
        except ValueError:
            rsrq = ""
        try:
            sinr = lte_info.get("sinr","")
            sinr = float(sinr)
        except ValueError:
            sinr = ""
        signal_summary["rsrp"] = self.get_word_from_map("RSRP",rsrp)
        signal_summary["rsrq"] = self.get_word_from_map("RSRQ",rsrq)
        signal_summary["sinr"] = self.get_word_from_map("SINR",sinr)
        signal_summary["rssi"] = self.get_word_from_map("RSSI",rssi)

        return signal_summary

    def template_lte_info(self,template):
        lte_info = self.get_lte_info()
        if len(lte_info)>0:
            lte_info = lte_info[0]
            signal_summary = self.get_signal_summary(lte_info)
            outstr = template.format(
                currentoperator=lte_info.get("current-operator",""),
                accesstechnology = lte_info.get("access-technology",""),
                primaryband = lte_info.get("primary-band",""),
                caband = lte_info.get("ca-band",""),
                rssi = signal_summary["rssi"],
                rssivalue = lte_info.get("rssi"),
                rsrp = signal_summary["rsrp"],
                rsrpvalue = lte_info.get("rsrp"),
                rsrq = signal_summary["rsrq"],
                rsrqvalue = lte_info.get("rsrq"),
                sinr = signal_summary["sinr"],
                sinrvalue = lte_info.get("sinr")
            )
            print(outstr)

    def display_lte_info(self):
        lte_info = self.get_lte_info()
        if len(lte_info)>0:
            lte_info = lte_info[0]
            signal_summary = self.get_signal_summary(lte_info)
            print("Current Operator:",lte_info.get("current-operator",""))
            print("Access Technology:",lte_info.get("access-technology",""))
            print("Primary Band:",lte_info.get("primary-band",""))
            print("CA  Band:",lte_info.get("ca-band",""))
            print("RSSI: %s (%s)" % (signal_summary["rssi"],lte_info.get("rssi")))
            print("RSRP: %s (%s)" % (signal_summary["rsrp"],lte_info.get("rsrp")))
            print("RSRQ: %s (%s)" % (signal_summary["rsrq"],lte_info.get("rsrq")))
            print("SINR: %s (%s)" % (signal_summary["sinr"],lte_info.get("sinr")))

    def get_current_simslot(self):
        api = self.get_api()
        slot = api.path('system','routerboard','modem')
        d = tuple(slot)
        return d[0]["sim-slot"]

    def set_current_simslot(self,slot):
        api = self.get_api()
        modem = api.path('system','routerboard','modem')
        params = {'sim-slot': slot}
        modem.update(**params)

    def switch_sim_slot(self):
        current_slot = self.get_current_simslot()
        new_slot = 'a' if current_slot=='b' else 'b'
        ok = timedinput.get_input(10,"Switch from sim slot %s to slot %s? (y/N)" % (current_slot,new_slot),"N")
        if not ok.upper()=="Y":
            print("Abort")
            return
        print("Switching")
        self.set_current_simslot(new_slot)
        ok = timedinput.get_input(180,"Stick with sim? (y/N)","N")
        if not ok.upper()=="Y":
            print("Reverting to original sim slot",current_slot)
            self.set_current_simslot(current_slot)

def test_get_word():
    lw = ltewatch()
    print(lw.get_word_from_map("RSRP",-105))
    print(lw.get_word_from_map("RSRP",-95))
    print(lw.get_word_from_map("RSRP",-85))
    print(lw.get_word_from_map("RSRP",-75))
    print(lw.get_word_from_map("RSRQ",-25))
    print(lw.get_word_from_map("RSRQ",-17))
    print(lw.get_word_from_map("RSRQ",-12))
    print(lw.get_word_from_map("RSRQ",-5))
    print(lw.get_word_from_map("SINR",-2))
    print(lw.get_word_from_map("SINR",10))
    print(lw.get_word_from_map("SINR",15))
    print(lw.get_word_from_map("SINR",25))

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s','--switch', help='Switch to other sim slot',action="store_true")
    group.add_argument('-m','--html', help='Use builtin html template',action="store_true")
    group.add_argument('-t','--template', help='File to load template from',type=str)
    args = parser.parse_args()
    if args.html:
        template = html_template
    elif args.template:
        f = open(args.template)
        template = f.read()
        f.close()
    else:
        template = stdout_template
        
    lw = ltewatch()
    if args.switch:
        lw.switch_sim_slot()
    else:
        lw.template_lte_info(template)
