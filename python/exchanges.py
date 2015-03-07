import sys
import json
import hmac
import time
import urllib
import urllib2
import hashlib
import httplib
import datetime

class Exchange(object):
  def __init__(self, domain):
    self._domain = domain
    self._shift = 1

  def get(self, method, params = None, headers = None):
    if not params: params = ''
    if not headers: headers = {}
    connection = httplib.HTTPSConnection(self._domain, timeout=60)
    connection.request('GET', method, params, headers = headers)
    response = connection.getresponse().read()
    return json.loads(response)

  def post(self, method, params, headers = None):
    if not headers: headers = {}
    connection = httplib.HTTPSConnection(self._domain, timeout=60)
    connection.request('POST', method, params, headers)
    response = connection.getresponse().read()
    return json.loads(response)


class Poloniex(Exchange):
  def __init__(self):
    super(Poloniex, self).__init__('poloniex.com/tradingApi')

  def __repr__(self): return "poloniex"

  def create_request(self, unit, secret = None):
    if not secret: return None, None
    request = { 'command' : 'returnOpenOrders', 'nonce' : int((time.time() + self._shift) * 1000),  'currencyPair' : "%s_NBT"%unit.upper()}
    data = urllib.urlencode(request)
    sign = hmac.new(secret, data, hashlib.sha512).hexdigest()
    return request, sign

  def validate_request(self, key, data, sign):
    headers = { 'Sign' : sign, 'Key' : key }
    ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/tradingApi', urllib.urlencode(data), headers))
    response = json.loads(ret.read()) #self.post('returnOpenOrders', urllib.urlencode(data), headers)
    if 'error' in response: return None
    return [ {
      'id' : int(order['orderNumber']),
      'price' : float(order['rate']),
      'type' : 'ask' if order['type'] == 'sell' else 'bid',
      'amount' : float(order['amount']),
      } for order in response ]