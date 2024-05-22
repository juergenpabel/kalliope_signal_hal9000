import paho.mqtt.publish as mqtt_publish

from kalliope.core import SignalModule, MissingParameter

from kalliope.core.ConfigurationManager import BrainLoader
from kalliope.core.SynapseLauncher import SynapseLauncher
from kalliope.core import Utils


class Hal9000(SignalModule):
	def __init__(self, **kwargs):
		super(Hal9000, self).__init__(**kwargs)
		for synapse in list(super(Hal9000, self).get_list_synapse()):
			for signal in synapse.signals:
				if signal.name == 'hal9000':
					for neuron in synapse.neurons:
						if neuron.name == 'mqtt_publisher':
							mqtt_publish.single(neuron.parameters['topic'], "starting", hostname=neuron.parameters['broker_ip'])

	def start(self):
		pass

	@staticmethod
	def check_parameters(parameters):
		return True

	def on_notification_received(self, notification=None, payload=None):
		pass

