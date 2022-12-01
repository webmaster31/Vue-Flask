from configparser import ConfigParser

cf = ConfigParser()

cf.read('setup.cfg')

print(f"API running at version: {cf['metadata']['version']}")
