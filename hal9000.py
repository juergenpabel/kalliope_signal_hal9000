from time import sleep
from threading import Thread
from paho.mqtt import client as mqtt_client
import logging

from kalliope.core import SignalModule, MissingParameter
from kalliope.core.Cortex import Cortex
from kalliope.core import Utils

logging.basicConfig()
logger = logging.getLogger("kalliope")

class Hal9000(SignalModule, Thread):
	def __init__(self, **kwargs):
		super(Hal9000, self).__init__(**kwargs)
		Thread.__init__(self, name=Hal9000)
		self.mqtt_broker_ip = '127.0.0.1'
		self.mqtt_broker_port = 1883
		self.mqtt_client_id = 'kalliope:signal:hal9000'
		self.mqtt_topic = 'hal9000/event/kalliope/interface/state'
		for synapse in list(super(Hal9000, self).get_list_synapse()):
			for signal in synapse.signals:
				if signal.name == 'hal9000' and signal.parameters is not None:
					self.mqtt_broker_ip = signal.parameters.get('broker_ip', self.mqtt_broker_ip)
					self.mqtt_broker_port = signal.parameters.get('port', self.mqtt_broker_port)
					self.mqtt_client_id = signal.parameters.get('client_id', self.mqtt_client_id)
					self.mqtt_topic = signal.parameters.get('topic', self.mqtt_topic)
		Cortex.save('kalliope_status', 'starting')

	def run(self):
		Utils.print_info('[Hal9000] Starting thread')
		try:
			mqtt = mqtt_client.Client(self.mqtt_client_id)
			mqtt.connect(self.mqtt_broker_ip, self.mqtt_broker_port)
			while Cortex.get_from_key('kalliope_status') == 'starting':
				mqtt.publish(self.mqtt_topic, 'starting')
				mqtt.loop(timeout=0.5)
				sleep(0.5)
			mqtt.disconnect()
			mqtt.loop_forever()
		except BaseException as e:
			logger.info(f"[signal:hal9000] {e}")
		Utils.print_info('[Hal9000] Ending thread')

	@staticmethod
	def check_parameters(parameters):
		return True

	def on_notification_received(self, notification=None, payload=None):
		pass

