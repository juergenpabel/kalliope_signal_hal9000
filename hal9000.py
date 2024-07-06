from time import sleep as time_sleep
from threading import Thread as threading_Thread
from paho.mqtt import client as paho_mqtt_client
import logging

from kalliope.core import SignalModule, MissingParameter
from kalliope.core.Cortex import Cortex
from kalliope.core.OrderListener import OrderListener
from kalliope.core import Utils

logging.basicConfig()
logger = logging.getLogger("kalliope")


class Hal9000(SignalModule, threading_Thread):
	def __init__(self, **kwargs):
		super(Hal9000, self).__init__(**kwargs)
		threading_Thread.__init__(self, name=Hal9000)
		self.mqtt_broker_ip = '127.0.0.1'
		self.mqtt_broker_port = 1883
		self.mqtt_client_id = 'kalliope:signal:hal9000'
		self.mqtt_topic = 'hal9000/event/kalliope/status'
		self.stt_warmup_filename = None
		for synapse in list(super(Hal9000, self).get_list_synapse()):
			for signal in synapse.signals:
				if signal.name == 'hal9000' and signal.parameters is not None:
					self.mqtt_broker_ip = signal.parameters.get('broker_ip', self.mqtt_broker_ip)
					self.mqtt_broker_port = signal.parameters.get('port', self.mqtt_broker_port)
					self.mqtt_client_id = signal.parameters.get('client_id', self.mqtt_client_id)
					self.mqtt_topic = signal.parameters.get('topic', self.mqtt_topic)
					self.stt_warmup_filename = signal.parameters.get('stt_warmup_filename', self.stt_warmup_filename)
		Cortex.save('kalliope_status', 'starting')


	def run(self):
		Utils.print_info('[Hal9000] Starting thread')
		try:
			mqtt = paho_mqtt_client.Client(self.mqtt_client_id)
			mqtt.connect(self.mqtt_broker_ip, self.mqtt_broker_port)
			while Cortex.get_from_key('kalliope_status') == 'starting':
				mqtt.publish(self.mqtt_topic, 'starting')
				mqtt.loop(timeout=0.5)
				time_sleep(0.5)
			mqtt.disconnect()
			mqtt.loop_forever()
		except BaseException as e:
			logger.error(f"[signal:hal9000] {e}")
		if self.stt_warmup_filename is not None:
			if os_path_exists(self.stt_warmup_filename) is True:
				Utils.print_info('[Hal9000] Pre-loading STT language model...')
				logger.debug(f"[signal:hal9000] using '{self.stt_warmup_filename}' for STT pre-loading of language model")
				ol = OrderListener(callback=self.stt_callback, audio_file_path=self.stt_warmup_filename)
				ol.start()
				ol.join()
				Utils.print_info('[Hal9000] Pre-loading STT language model completed')
			else:
				logger.warning(f"[signal:hal9000] configured stt_warmup_filename ('{self.stt_warmup_filename}') not found, skipping STT pre-loading of language model")
		Cortex.save('kalliope_status', 'ready')
		logger.info(f"[signal:hal9000] startup finished")
		Utils.print_info('[Hal9000] Ending thread')


	def stt_callback(self, order):
		pass


	@staticmethod
	def check_parameters(parameters):
		return True


	def on_notification_received(self, notification=None, payload=None):
		pass

