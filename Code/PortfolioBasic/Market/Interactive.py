from ib.opt import ibConnection, Connection, message
from ib.ext.Contract import Contract
import time
'''pip install git+git://github.com/blampe/IbPy.git
'''


class IBDataCollector:

  def __init__(self, contract: Contract, date, t, duration):
    self.contract = contract
    self.date = date
    self.t = t
    self.duration = str(duration) + ' S'
    self.tick_id = 1
    self.con = Connection.create(port=7496, clientId=999)
    self.con.register(self.process_data, message.historicalData)
    self.con.registerAll(self.watchAll)
    print(self.con.connect())
    time.sleep(1)
    end_datetime = ('%s %s US/Eastern' % (self.date, self.t))
    self.con.req
    self.con.reqHistoricalData(tickerId=self.tick_id, contract=self.contract, endDateTime=end_datetime,
                               durationStr='1 W', barSizeSetting='1 day', whatToShow='TRADES',
                               useRTH=0, formatDate=1)
    self.data_received = False

  def close(self):
    while not self.data_received:
      pass
    self.con.cancelHistoricalData(self.tick_id)
    time.sleep(1)
    self.con.disconnect()
    time.sleep(1)

  def process_data(self, msg):
    if msg.open != -1:
      print(self.outfile, msg.date, msg.open, msg.high, msg.low, msg.close, msg.volume, msg.count, msg.WAP, msg.hasGaps)
    else:
      self.data_received = True

  def watchAll(self, msg):
    print(msg)