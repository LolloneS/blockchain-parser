#!/usr/bin/env python3 

from __future__ import unicode_literals
from gunicorn.six import iteritems
from pbbp.blockchain_parser.blockchain import Blockchain
from flask import Flask, render_template, make_response, request, Response
import gunicorn.app.base
import multiprocessing
import os
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

# def number_of_workers():
#     return (multiprocessing.cpu_count() * 2) + 1

app = Flask(__name__)

blockchain = Blockchain(os.path.expanduser('~/.bitcoin/blocks'))

@app.route('/')
def index():
    return render_template('index.html')

class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


# txid prova
# 8eb078510f7a1b4272712a43ddaa299802e22be68cc3e36160491a338de0178e
# 6588c4f08934e0ff7e3bcb4cfc5973b5293be9e2a6167712902b4dc7b5df518b



# redis syntax
# [0/1, is_segwit, (), (), ()]

def get_tx_from_redis(t_id):
    if r.llen(t_id) > 0: 
        s = ''
        count = 0
        has_problems = True if int(r.lindex(t_id, count).decode()) == 1 else False
        count += 1
        s += "<b> Is segwit? </b>: {} <br>".format(r.lindex(t_id, count).decode())
        s += "<b> Outputs</b>: <ul>"
        if not has_problems:
            while r.llen(t_id) > 2 and r.llen(t_id) - count > 1:
                count += 1
                s += '<li>'
                s += r.lindex(t_id, count).decode()
                s += ' to address  '
                count += 1
                s += r.lindex(t_id, count).decode()
                s += '</li>\n'
        else:
            while r.llen(t_id) - count > 1:
                count += 1
                s += '<li>'
                s += r.lindex(t_id, count).decode()
                s += '</li>\n'
            s += '</ul>'
        return s
    return None

@app.route('/search', methods=['GET', 'POST'])
def search_for_transactions():
    t_id = request.form.get('t_id').strip()
    cached_tx = get_tx_from_redis(t_id)
    if cached_tx != None:
        print("Found and was cached!")
        return cached_tx
    else:
        for block in blockchain.get_unordered_blocks():
            for tx in block.transactions:
                amnts, addrs, broken = [], [], False
                if r.llen(tx.txid) <= 0: 
                    r.rpush(tx.txid, "YES" if tx.is_segwit else "NO")
                    for elem in tx.outputs:
                        amnts.append(str(elem.value))
                        if broken == False:
                            try:
                                x = elem.addresses[0].address
                                addrs.append(x)
                            except:
                                broken = True
                    if not broken:
                        r.lpush(tx.txid, 0)
                        for i in range(len(addrs)):                    
                            r.rpush(tx.txid, amnts[i])
                            r.rpush(tx.txid, addrs[i])
                    if broken:
                        r.lpush(tx.txid, 1)
                        for i in range(len(addrs)):                    
                            r.rpush(tx.txid, amnts[i]) 
                if tx.txid == t_id:
                    print("Found and wasn't cached!")
                    return get_tx_from_redis(t_id)
                        
    return "There was a problem while processing the request."




if __name__ == '__main__':
    options = {
        'bind': '%s:%s' % ('192.168.1.1', '8080'), # This becomes 192.168.1.1 on the lab VM    
        # 'workers': number_of_workers(),
        'workers' : 1,
        'timeout': 100000
    }

StandaloneApplication(app, options).run()
