from scanner import config
from scanner.calculator.chain import Chain


def compute():
    chain = Chain(config.get_config().get('wled_led_count'))

    chain.compute_points()
