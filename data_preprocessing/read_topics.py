from gensim.test.utils import datapath
from gensim.models.ldamulticore import LdaMulticore

m = LdaMulticore.load("model5.gensim")

topics = m.print_topics(num_words=20)
print(len(topics))
for topic in topics:
    print(topic)
