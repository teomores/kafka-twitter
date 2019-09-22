import spacy
from spacy.lang.en import English
"""
import nltk
import ssl
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
"""
from gensim.corpora import Dictionary
import random
import pandas as pd
from gensim import corpora
import pickle
import gensim
from tqdm import tqdm
import os
from gensim import models

DOWNLOAD_WORDLISTS = False


def tokenize(text):
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            #lda_tokens.append('URL')
            pass
        elif token.orth_.startswith('RT'):
            pass
        elif token.orth_.startswith('@'):
            #lda_tokens.append('SCREEN_NAME')
            pass
        else:
            lda_tokens.append(token.lower_)

    return lda_tokens

def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma

def get_lemma2(word):
    return WordNetLemmatizer().lemmatize(word)

def prepare_text_for_lda(text):
    text = str(text)
    tokens = tokenize(text)
    tokens = [token for token in tokens if len(token) > 4]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [get_lemma(token) for token in tokens]
    return tokens

def tweet_cleaner(tweets):
    new_tweets = []
    for t in tqdm(tweets):
        if ('@' not in t) and ('http' not in t):
            new_tweets.append(t)
    return new_tweets


if __name__=='__main__':
    """
    if DOWNLOAD_WORDLISTS:
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        nltk.download()
        nltk.download('wordnet')
        nltk.download('stopwords')


    stopwords = nltk.corpus.stopwords.words('english')
    my_stopwords = ['could', 'would', 'always', 'still', 'never', 'ever','literally','going']
    for w in my_stopwords:
        stopwords.append(my_stopwords)
    en_stop = stopwords
    spacy.load('en')
    parser = English()
    text_data = []

    #prepare the dataset in one large pandas dataframe
    COLUMN_NAMES = ['user', 'text', 'hashtags', 'mentions']
    dataset = pd.DataFrame(columns=COLUMN_NAMES)

    files = pd.read_csv('data/twitter_dataset.csv', lineterminator='\n')

    f = files['text'].tolist()
    tweets = tweet_cleaner(f)
    count = 0
    for line in tqdm(tweets):
        count=count+1
        tokens = prepare_text_for_lda(line)

        while 'SCREEN_NAME' in tokens:
            tokens.remove('SCREEN_NAME')
        while 'would' in tokens:
            tokens.remove('would')
        while 'still' in tokens:
            tokens.remove('still')
        while 'ever' in tokens:
            tokens.remove('ever')
        while 'every' in tokens:
            tokens.remove('every')
        while 'never' in tokens:
            tokens.remove('never')
        while 'first' in tokens:
            tokens.remove('first')
        text_data.append(tokens)

    #here the magic begins
    dictionary = corpora.Dictionary(text_data)

    corpus = [dictionary.doc2bow(text) for text in text_data]

    pickle.dump(corpus, open('corpus.pkl', 'wb'))
    dictionary.save('dictionary.gensim')

    NUM_TOPICS = 20

    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics = NUM_TOPICS, id2word=dictionary, passes=15)
    ldamodel.save('model5.gensim')

    topics = ldamodel.print_topics(num_words=1)
    print(len(topics))
    for topic in topics:
        print(topic)
    """
    from gensim.models.ldamulticore import LdaMulticore
    parser = English()
    ldamodel = LdaMulticore.load("model5.gensim")
    dictionary = corpora.Dictionary
    dictionary.load('dictionary.gensim')


    new_doc = 'Math is very important'
    new_doc = prepare_text_for_lda(new_doc)
    new_doc_bow = dictionary.doc2bow(new_doc)
    print(new_doc_bow)
    print(ldamodel.get_document_topics(new_doc_bow))
