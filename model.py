import multiprocessing
import os
from time import time
import logging
from sklearn.model_selection import train_test_split
import pandas as pd
from gensim.models.doc2vec import TaggedDocument
from ufal.udpipe import Model, Pipeline # pylint disable
import nltk
from gensim.models import Doc2Vec

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def log(msg):
    print(msg)
    logging.info(msg)


class Doc2VecModel:
    modes = {
        0: 'build vocab',
        1: 'train model',
        2: 'predict'
    }

    default_model_options = {
        'dm': 1,
        'size': 150,
        'negative': 5,
        'hs': 0,
        'min_count': 2,
        'workers': multiprocessing.cpu_count(),
        'numpasses': 10,
        'numiter': 10
    }

    def __init__(self, mode=0, tag='test', data_file='decisions_min.csv', options=None):
        """
        init
        :param dm: алгоритм. 0 = PV-DBOW, 1 = PV-DM. default=1
        :param mode: 0 - build vocab, 1 - train model, 2 - predict. default=0
        """
        self.mode = mode if mode in self.modes else 0
        self.model_options = options or self.default_model_options
        self.tag = tag
        self.data_file = data_file

        self.model = None
        self.udpipe_model = None
        self.test_sents = None

        self.tagged_counter = 0
        self.tagged_max = 0

    def run(self):
        log(f'Run, mode: {self.modes[self.mode]}')
        df = self._get_data(self.data_file)
        train, test = train_test_split(df, test_size=0.2, random_state=42)

        log('Create train tagged documents')
        self.tagged_counter = 0
        self.tagged_max = train.shape[0]
        train_tagged = train.apply(lambda r: TaggedDocument(words=self._tokenize(r['text']), tags=[r.court]), axis=1)

        log('Create test tagged documents')
        self.tagged_counter = 0
        self.tagged_max = test.shape[0]
        test_tagged = test.apply(lambda r: TaggedDocument(words=self._tokenize(r['text']), tags=[r.court]), axis=1)

        log('Create model')
        self.model = Doc2Vec(**self.model_options)
        print(self.model)

        self._build_vocab(train_tagged)
        self._save_vocab()
        self._train(train_tagged, test_tagged)
        self._save_model()

    def _build_vocab(self, tagged):
        log('Build vocab')
        self.model.build_vocab([x for x in tagged.values])
        log(f'Vocab is builded, len: {len(self.model.wv.vocab)}')

    def _save_vocab(self):
        vocab_path = os.path.join(BASE_DIR, 'vocab', f'{self.tag}.vocab')
        log(f'Save vocabulary to: {vocab_path}')
        self.model.wv.save(vocab_path)

    def _save_model(self):
        model_path = os.path.join(BASE_DIR, 'model', f'{self.tag}_d2w.model')
        log(f'Save model to: {model_path}')
        self.model.wv.save(model_path)

    def _train(self, train_tagged, test_tagged):
        from sklearn import utils as skutils
        from utils import vec_for_learning
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, f1_score

        model = self.model
        for epoch in range(30):  # pylint: disable no-unused-vars
            model.train(skutils.shuffle([x for x in train_tagged.values]), total_examples=len(train_tagged.values), epochs=1)
            model.alpha -= 0.002
            model.min_alpha = model.alpha

        y_train, x_train = vec_for_learning(model, train_tagged)
        y_test, x_test = vec_for_learning(model, test_tagged)

        logreg = LogisticRegression(n_jobs=1, C=1e5)
        logreg.fit(x_train, y_train)
        y_pred = logreg.predict(x_test)

        log('Testing accuracy %s' % accuracy_score(y_test, y_pred))
        log('Testing F1 score: {}'.format(f1_score(y_test, y_pred, average='weighted')))

    @staticmethod
    def _get_data(data_file):
        log('Read data...')
        data_path = os.path.join(BASE_DIR, 'data', data_file)
        df = pd.read_csv(data_path, delimiter=';', header=None, names=['text', 'court'])
        df = df[['text', 'court']]

        return df[pd.notnull(df['text'])]

    def _tokenize(self, text='Текст нужно передать функции в виде строки!'):
        from utils import lemmatize

        if not self.udpipe_model:
            udpipe_model_path = os.path.join(BASE_DIR, 'model', 'udpipe_syntagrus.model')

            if not os.path.isfile(udpipe_model_path):
                msg = 'UDPipe model not found!'
                logging.critical(msg)
                raise IOError(msg)

            self.udpipe_model = Model.load(udpipe_model_path)

        t = time()
        process_pipeline = Pipeline(self.udpipe_model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')

        result = []
        for line in nltk.sent_tokenize(text):
            # line = unify_sym(line.strip()) # здесь могла бы быть ваша функция очистки текста
            output = lemmatize(process_pipeline, text=line)
            result.extend(output)

        self.tagged_counter += 1
        log(f'{self.tagged_counter} of {self.tagged_max} created, for {round(time() - t, 2)}s')

        return result


if __name__ == '__main__':
    log_path = os.path.join(BASE_DIR, 'logs.log')
    logging.basicConfig(
        filename=log_path,
        format=u'%(levelname)s - %(asctime)s: %(message)s',
        datefmt='%H:%M:%S', filemode='w', level=logging.DEBUG
    )

    model_opts = {
        'dm': 1,
        'dm_mean': 1,
        'vector_size': 300,
        'window': 10,
        'negative': 5,
        'min_count': 1,
        'workers': multiprocessing.cpu_count(),
        'alpha': 0.065,
        'min_alpha': 0.065
    }

    model = Doc2VecModel(tag='test_max', data_file='decisions.csv', options=model_opts)
    model.run()
