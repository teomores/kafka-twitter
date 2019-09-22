from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
from tqdm import tqdm
import pandas as pd


class Tweet2Vec(object):

    def __init__(self, vec_size, max_epochs):
        self.max_epochs = max_epochs
        self.model = Doc2Vec(vector_size=vec_size,
                             alpha=0.025,
                             min_alpha=0.00025,
                             min_count=1,
                             dm=1,
                             workers=4)

    def train_model(self, docs, save=False):
        tagged_data = [TaggedDocument(words=word_tokenize(d.lower()), tags=[str(i)]) for i, d in enumerate(docs)]

        self.model.build_vocab(tagged_data)

        for epoch in tqdm(range(self.max_epochs), desc="Epochs"):
            self.model.train(tagged_data,
                             total_examples=self.model.corpus_count,
                             epochs=self.model.iter)

            # Decrease the learning rate
            self.model.alpha -= 0.0002
            # Fix the learning rate, no decay
            self.model.min_alpha = self.model.alpha
            # Save model
            if save:
                self.model.save("d2v.model")


if __name__ == '__main__':
    # Example documents
    docs = ["I love machine learning. Its awesome.",
            "I love coding in python",
            "I love building chatbots",
            "they chat amagingly well"]

    # Load tweets
    df = pd.read_csv('data/twitter_dataset.csv', lineterminator='\n')
    tweets = df['text'].tolist()[:100]

    # Train model
    t2v = Tweet2Vec(20, 100)
    t2v.train_model(tweets)

    # Get all vectors
    vectors = [list(t2v.model.docvecs[str(i)]) for i, d in enumerate(tweets)]
    print(vectors)

    # Find vector of a document in the training data
    v = t2v.model.docvecs['0']
    print(v)

    # Infer vector of a document not in training data
    test_data = word_tokenize("I love math!".lower())
    v = t2v.model.infer_vector(test_data)
    print(v)

    # Find most similar docs using tag
    similar_docs = t2v.model.docvecs.most_similar('1')
    print(similar_docs)

