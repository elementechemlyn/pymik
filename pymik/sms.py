import ssl
import argparse
import re
from datetime import datetime

import librouteros
import mktconfig

class sms(object):
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

    def send_sms(self,number,message):
        api = self.get_api()
        try:
            #p('send',**{'phone-number':'+12345667','message':'is this a message?'})
            sms = api.path('tool','sms')
            r = sms('send',**{'phone-number':number,'message':message})
            return tuple(r)
        except librouteros.exceptions.TrapError:
            return None

    def load_inbox(self):
        api = self.get_api()
        try:
            inbox = api.path('tool','sms','inbox')
            return tuple(inbox)
        except librouteros.exceptions.TrapError:
            return None

    def fix_up_date(self,date_str):
        match = re.match('(^.+?[\+\-])([0-9]+)$',date_str)
        offset = '0' + match.group(2) if len(match.group(2))==1 else match.group(2)
        offset = offset + ':00'
        return match.group(1) + offset

    def sort_inbox(self,inbox:list):
        inbox.sort(key=lambda x:x['timestamp'],reverse = True)
        return inbox

    def delete_message(self,msg):
        pass

    def save_message(self,msg):
        pass

    def get_inbox(self):
        messages = self.load_inbox()
        msg_by_ts = {}
        inbox = []
        for message in messages:
            key = "%s_%s" % (message['timestamp'],message['phone'])
            if key in msg_by_ts:
                msg_by_ts[key].append(message)
            else:
                msg_by_ts[key] = [message,]
        for ts in msg_by_ts.keys():
            msgs = msg_by_ts[ts]
            sender = ''
            txt = ''
            for msg in msgs:
                if sender=='':
                    sender = msg['phone']
                elif not sender == msg['phone']:
                    raise ValueError('%s sender does not match group %s' % (msg['phone'],sender))
                txt = txt + msg['message']
                iso_ts = self.fix_up_date(msg['timestamp'])
                iso_dt = datetime.strptime(iso_ts,'%b/%d/%Y %H:%M:%S %Z %z')
            inbox.append({'sender':sender,'messge':txt,'timestamp':iso_dt})
        return self.sort_inbox(inbox)

if __name__=="__main__":
    pass
    """
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
    """