from os.path import exists as os_path_exists
from time import sleep as time_sleep
from threading import Thread as threading_Thread
from paho.mqtt import client as paho_mqtt_client
import logging

from kalliope.core import SignalModule, MissingParameter
from kalliope.core.Cortex import Cortex
from kalliope.core.OrderListener import OrderListener
from kalliope.core.NotificationManager import NotificationManager
from kalliope.core import Utils

logging.basicConfig()
logger = logging.getLogger("kalliope")


class Hal9000(SignalModule, NotificationManager, threading_Thread):
	def __init__(self, **kwargs):
		SignalModule.__init__(self, **kwargs)
		NotificationManager.__init__(self)
		threading_Thread.__init__(self, name=Hal9000)
		self.mqtt_broker_ip = '127.0.0.1'
		self.mqtt_broker_port = 1883
		self.mqtt_client_id = 'kalliope:signal:hal9000'
		self.mqtt_topic = 'hal9000/event/kalliope/runlevel'
		for synapse in list(super(Hal9000, self).get_list_synapse()):
			for signal in synapse.signals:
				if signal.name == 'hal9000' and signal.parameters is not None:
					self.mqtt_broker_ip = signal.parameters.get('broker_ip', self.mqtt_broker_ip)
					self.mqtt_broker_port = signal.parameters.get('port', self.mqtt_broker_port)
					self.mqtt_client_id = signal.parameters.get('client_id', self.mqtt_client_id)
					self.mqtt_topic = signal.parameters.get('topic', self.mqtt_topic)
		Cortex.save('kalliope_runlevel', 'starting')


	def run(self):
		Utils.print_info('[Hal9000] Starting thread')
		try:
			mqtt = paho_mqtt_client.Client(self.mqtt_client_id)
			mqtt.connect(self.mqtt_broker_ip, self.mqtt_broker_port)
			mqtt.will_set(self.mqtt_topic, 'killed')
			while Cortex.get_from_key('kalliope_runlevel') == 'starting':
				mqtt.publish(self.mqtt_topic, 'starting')
				mqtt.loop(timeout=0.5)
				time_sleep(0.5)
			mqtt.loop_forever()
		except BaseException as e:
			logger.error(f"[signal:hal9000] {e}")
		Utils.print_info('[Hal9000] Ending thread')


	def stt_callback(self, order):
		pass


	@staticmethod
	def check_parameters(parameters):
		return True


	def on_notification_received(self, notification=None, payload=None):
		if notification == 'hal9000_stt_warmup':
			stt_wav_filename = None
			if 'filename' in payload:
				stt_wav_filename = payload['filename']
			if stt_wav_filename is not None:
				if os_path_exists(stt_wav_filename) is True:
					logger.info(f"[signal:hal9000] Pre-loading STT language model with '{stt_wav_filename}'...")
					ol = OrderListener(callback=self.stt_callback, audio_file_path=stt_wav_filename)
					ol.start()
					ol.join()
					logger.info('[signal:hal9000] Pre-loading STT language model finished')
				else:
					logger.warning(f"[signal:hal9000] configured filename ('{stt_wav_filename}') not found, " \
					               f"not pre-loading language model")

