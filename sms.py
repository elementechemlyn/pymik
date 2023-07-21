import ssl
import argparse

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