import pandas as pd
import time
import random
import requests

df_twitter_dataset = pd.read_csv('data_preprocessing/data/twitter_dataset.csv', lineterminator='\n')
print(df_twitter_dataset.head(5))
df_twitter_dataset = df_twitter_dataset.head(100)

# poche città per semplicità
location_list = ['Milano', 'Firenze', 'Roma','Napoli', 'Torino']
tweet_text = ['NEW FUNCTIONALITY COMING SOON', 'Check it out ->', 'This is awesome!', 'Exam day',
    'Help please...','Am I in a live streaming simulation?', 'Just another day at PoliMi', 'Middleware presentation today :)']
hashtags = ['#mondayexamday ','#middleware ','#apache ','#kafka ', '#openmp','#mpi','#apachekafka ','#confluent ', '#akka ', '#akkaactors ', '#flask ','#python ']
mentions = ['@teomore','@alessiorussointroito','@tmscarla','@polimiofficial']
for t in df_twitter_dataset['user']:
    wait = random.uniform(0, 2)
    time.sleep(wait)
    data = {
        'id': f"{t}",
        'content': f"{random.choice(tweet_text)} {random.choice(hashtags)} {random.choice(mentions)}",
        "timestamp": time.time(),
        'location': random.choice(location_list)
    }
    r = requests.post("http://127.0.0.1:5000/tweet",data=data, cookies={'username':'teo'})
    print(r.text)
