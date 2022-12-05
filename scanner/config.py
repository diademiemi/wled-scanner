import yaml

config_file = 'config.yaml'


def get_config():
    with open('config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    return config
