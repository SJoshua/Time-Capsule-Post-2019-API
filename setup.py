# coding: utf-8

import sys
from setuptools import setup, find_packages
import mysql.connector
from config import cfg

db = mysql.connector.connect(
	host = cfg["host"],
	user = cfg["user"],
	passwd = cfg["passwd"],
	database = cfg["database"]
)

cur = db.cursor()
cur.execute("ALTER TABLE `%s`.`question_capsules` ADD `new_message` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL ;" % cfg["database"])
cur.close()
db.close()

##########################################

NAME = "swagger_server"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["connexion"]

setup(
    name=NAME,
    version=VERSION,
    description="Time Capsule Post 2019 API",
    author_email="joshuasrkf@gmail.com",
    url="",
    keywords=["Swagger", "Time Capsule Post 2019 API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    For Time Capsule 2019. Please call WeChat API for authorization first.
    """
)
