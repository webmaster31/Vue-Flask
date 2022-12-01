from configparser import ConfigParser

cf = ConfigParser()

cf.read('setup.cfg')

print(f"Worker running at version: {cf['metadata']['version']}")
