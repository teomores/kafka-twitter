<p align="center">
<img height=180px src="https://github.com/teomores/kafka-twitter/blob/master/logo.jpg"/>
</p>

# Kafka Twitter

<img src="https://img.shields.io/github/license/teomores/kafka-twitter"/> <img src="https://img.shields.io/github/issues/teomores/kafka-twitter"/> <img src="https://img.shields.io/github/stars/teomores/kafka-twitter"/> 

Repository for the mandatory project for the 2019 **Middleware Technologies** class.

The purpose of  this project is to implement a simplified version of the Twitter social network using **Apache Kafka** to store tweets. Users interact with Twitter using a client that presents a timeline of tweets and allows users to publish new tweets.

The scope of the project was to create a dummy version of the popular Twitter social network. In our case, we developed a very simple application that has 3 main components:
1. **Client**: the user will interact with the app through a basic GUI made with Tkinter
2. **Application Server**: this component will receive the REST calls from the client and will forward them to the Kafka Brokers in order to publish or fetch the messages. This component is also responsible for filtering the messages. We used Flask to map the REST API.
3. **Kafka**: we used Apache Kafka to store the tweets. Our specific setup was made of 1 machine running both Zookeeper and Kafka, and 2 machines as additional Kafka brokers.

Even if it was not requested, we wanted to reproduce a real life situation by using
real tweets of real users. To reach this goal, in the <code>data_preprocessing</code>
folder there the scripts used in order to get, clean and prepare the final dataset; in particular:
1. `tweet_api.py`: this was used in order to periodically fetch tweets from the Twitter social network by means of the Twitter API accessed through the [Twython wrapper](https://twython.readthedocs.io/en/latest/).
2. `topic_extraction.py`: this script extracts the topics from the tweets previously gathered, producing an **LDA model** that will be used in order to assign a topic to each new tweet in the social network. To performa LDA, we used the very cool free python library [gensim](https://radimrehurek.com/gensim/) together with [nltk](https://www.nltk.org/). A detailed and interesting tutorial can be found in [this article](https://towardsdatascience.com/topic-modelling-in-python-with-nltk-and-gensim-4ef03213cd21).

## Getting Started
In this paragraph, we'll see all the steps needed to get the project up and running on your local machine.
### Prerequisites
1. [Python 3.7.4](https://www.python.org/downloads/release/python-374/)
2. [Java 8](https://www.java.com/it/download/)

### Installing
#### 1. Local Setup
This is the basic setup if you want to run the application on a single machine. In this case your machine will host the client, the AppServer and both Kafka and Zookeeper. If you want to run the application in a distributed scenario, jump to the next section.

1. First of all, you need **Apache Kafka**. In order to do so, just follow the simple instructions provided on the [Confluent Platform Quick Start](https://docs.confluent.io/current/quickstart/ce-quickstart.html#ce-quickstart) page. In a few minutes you should be able download and setup all you need; at that point just open your favorite terminal and run:
```console
foo@bar:~$ <PATH-TO-CONFLUENT>/bin/confluent local start
```
And that's it with Kafka, as simple as that :)

2. The **Application Server** will serve all the REST calls of the clients so it's the first thing that has to be started. In order to do open the `Server.py` file and jump to lat lines of the code. You should see something like:
```python
if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)
```
Edit this properties as you please. The parameter names are pretty self-explanatory, but just to be sure...
- fill the `host` with the IP machine that will run your server (note: if you are running the app just on your machine, you can simply leave the localhost).
- Flask typically runs on `port` 5000, but you can change this if you need it.
- `debug` is set to true so you can know what's going on.
3. Now simply go to the project folder run the following line on the shell and you should be good to go:
```console
foo@bar:~$ python3 Server.py
```
After a few seconds, your Application Server should be running.

Finally, run the `KafkaTwitter.py` script and enjoy this very basic streaming message application.

#### 2. Distributed Setup
The above procedure will work if you are planning to run the application on your machine. Connecting multiple machines will require a few additional steps:
1. First, since you need to connect the machines in a network, you'll need:
- to create a **LAN**
- to setup your **static IP**
There are quite a lot tutorials to do this, I will not cover this but from now on I'll assume that your machines have a unique static IP and are connected through a LAN.

2. **Apache Kafka**: to setup a Kafka Cluster between several machines simply follow the instructions to setup [Confluent Kafka](https://docs.confluent.io/current/quickstart/ce-quickstart.html#ce-quickstart) on a single machine. In addition, go to the `<PATH-TO-CONFLUENT>/etc/kafka/` directory, you should see a `server.properties` file, you need to open it and edit a couple of things:
```console
foo@bar:~$ nano server.properties
```
There are quite a lot properties to play with, but for now we are interested only in 3:

- `broker.id=<YOUR_ID>` this parameter is required as a *unique broker identifier* for each machine running in the Kafka Cluster. There are no restrictions, you can choose whatever number you like as long as the brokers' IDs are all distinct.
- `listeners=PLAINTEXT://<YOUR_IP>:<YOUR_PORT>` this is pretty explicative, just put in your static IP and your favorite port. By default, if you haven't change it, Kafka brokers will run on port 9092.
- `zookeeper.connect=<MACHINE_RUNNING_ZK_IP>:<ZK_PORT>` fill the IP and port with the ones of the machine/machines running *Zookeeper* (the port is typically set on 2181). Note that if you plan to create a cluster with 3 machines, you'll need to create 3 instances of Kafka, one for each broker, but only one instance of Zookeeper. In general, the number of Zookeeper instances is an odd number, which allows Zookeeper to perform majority elections algorithms in order to elect the leader. In general, for small clusters 1 Zookeeper instance will be sufficient. Run the Zookeeper instance followed by the Kafka instances and your cluster should be good.

3. For what concerns the Application Server, edit the previous `host` and `port` properties with the ones of the machine that will run the `Server.py` script and then start the server on that machine.

4. Now you can run the `KafkaTwitter.py` script on each PC and start sharing messages  with your friends.

## Authors
- [**Matteo Moreschini**](https://github.com/teomores) - *chief of the project* (we presented 3 projects, each one of us took a leading role in one of them in particular, I was the leader of this one)
- [**Alessio Russo Introito**](https://github.com/russointroitoa) - *help with preprocessing and project planning*
- [**Tommaso Scarlatti**](https://github.com/tmscarla) - *help with preprocessing and project planning*

## License
This project is licensed under the Apache License 2.0.
