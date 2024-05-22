from time import sleep
from threading import Thread
import logging
import paho.mqtt.publish as mqtt_publish

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
		self.mqtt_topic = 'hal9000/event/kalliope/interface/state'
		for synapse in list(super(Hal9000, self).get_list_synapse()):
			for signal in synapse.signals:
				if signal.name == 'hal9000':
					for neuron in synapse.neurons:
						if neuron.name == 'mqtt_publisher':
							self.mqtt_broker_ip = neuron.parameters.get('broker_ip', self.mqtt_broker_ip)
							self.mqtt_broker_port = neuron.parameters.get('port', self.mqtt_broker_port)
							self.mqtt_topic = neuron.parameters.get('topic', self.mqtt_topic)
		Cortex.save('kalliope_status', 'starting')

	def run(self):
		Utils.print_info('[Hal9000] Starting thread')
		try:
			while Cortex.get_from_key('kalliope_status') == 'starting':
				mqtt_publish.single(self.mqtt_topic, 'starting', hostname=self.mqtt_broker_ip, port=self.mqtt_broker_port,
				                    client_id='kalliope-signal-hal9000')
				sleep(1)
		except BaseException as e:
			logger.info(f"[signal:hal9000] {e}")
		Utils.print_info('[Hal9000] Ending thread')

	@staticmethod
	def check_parameters(parameters):
		return True

	def on_notification_received(self, notification=None, payload=None):
		pass

