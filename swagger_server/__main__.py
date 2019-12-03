#!/usr/bin/env python3

import connexion
import logging

from swagger_server import encoder
from config import cfg

def main():
    logging.basicConfig(filename='log.log',level=logging.INFO)
    logging.info("Server started.")
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.app.secret_key = cfg["secret_key"]
    app.add_api('swagger.yaml', arguments={'title': 'Time Capsule Post 2019 API'}, pythonic_params=True)
    app.run(port=8080, debug=cfg["debug"])

if __name__ == '__main__':
    main()
