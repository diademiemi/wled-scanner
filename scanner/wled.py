import json

import requests as requests


class WLED:
    def __init__(self, ip, led_count):
        self.ip = ip
        self.led_count = led_count
        self.url = f'http://{self.ip}/json'
        self.headers = {'Content-Type': 'application/json'}

    def set_led(self, index, color=(255, 255, 255)):
        # Set LED to color
        payload = json.dumps({"seg": [{"id": 0, "i": [index - 1, color]}]})
        return requests.post(self.url, data=payload, headers=self.headers)

    def off(self):
        # Turn off all LEDs
        payload = json.dumps({"seg": [{"id": 0, "i": [0, self.led_count, [0, 0, 0]]}]})
        return requests.post(self.url, data=payload, headers=self.headers)

    def on(self, color=(255, 255, 255)):
        # Turn on all LEDs
        payload = json.dumps({"seg": [{"id": 0, "i": [0, self.led_count, color]}]})
        return requests.post(self.url, data=payload, headers=self.headers)
