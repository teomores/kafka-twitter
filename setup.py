from setuptools import setup

with open("README.md", 'r') as f:
    description = f.read()

setup(
   name='KafkaTwitter',
   version='1.0',
   description='A simple version of the famous social network made with Apache Kafka',
   license="Apache 2.0",
   long_description=description,
   author='Matteo Moreschini',
   author_email='matmoresc@gmail.com',
   packages=['kafka-twitter'],
   install_requires=[
   'six',
   'gensim',
   'colorama',
   'appscript',
   'keyboard',
   'requests',
   'nltk',
   'spacy',
   'tqdm',
   'twython',
   'confluent_kafka',
   'pandas',
   'avro'
   ]
)
