from db_data import get_train_courts, get_test_courts
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
from sklearn import utils
from sklearn.linear_model import LogisticRegression
from tqdm import tqdm  # бар
import re
import nltk
from nltk import sent_tokenize, word_tokenize
from sklearn.metrics import accuracy_score, f1_score
nltk.download('punkt')

################################################################################################
# получаем решения 80% на 20% для обучения и тренировки (вид [[текст, 3][текст, 3][текст, 3]]) #
################################################################################################

train_court = get_train_courts() # список словарей [(текст, 4)(текст, 3)(текст ,2)]
test_courts = get_test_courts()  # список словарей [(текст, 4)(текст, 3)(текст ,2)]

print(len(train_court), '  тренировочных записей')
print(len(test_courts), '  тестовых записей', '\n', 100*'-')


################################################################################################
# приводим тексты в к формату документов таги = 5, текст = [список слов]                       #
################################################################################################

def numerate_tag(non_numer): # функция приведения тага в порядок
    result = "None"
    if non_numer != None:
        count = len(non_numer)
        if count > 5:
            return result
        if count < 5:
            number = re.findall(r'\d+', non_numer)
            number = number[0]  
            result = number
    return result


def tokenize_text(text):  # функция токенизации текста на вход текст на выход список (не видно изменений)
    tokens = []
    for sent in nltk.sent_tokenize(text, language="russian"): 
        for word in nltk.word_tokenize(sent):
            # if len(word) < 2:
            #     continue
            tokens.append(word.lower())
    return tokens


def taged_docs(non_taget_text): # разметка документов
    result = []
    for text in non_taget_text:
        words = TaggedDocument(words=tokenize_text(text[0]), tags=numerate_tag(text[1]))
        result.append(words)
    return result


tagget_train = taged_docs(train_court) # список резмеченых экземпляров документов
print(len(tagget_train), 'tagged trains')
tagget_test = taged_docs(test_courts)
print(len(tagget_test), 'tagged tests')


################################################################################################
# создаем экземпляр класса и заполняем словарь                                                 #
################################################################################################


model_dmm = Doc2Vec(dm=1, dm_mean=1, vector_size=300, window=10, negative=5, min_count=1, workers=6, alpha=0.065, min_alpha=0.065)
model_dmm.build_vocab(tagget_train)

print('vocab builded')


for epoch in range(30):
    model_dmm.train(utils.shuffle(tagget_train), total_examples=len(tagget_train), epochs=1)
    model_dmm.alpha -= 0.002
    model_dmm.min_alpha = model_dmm.alpha
    print('Training epoh done')


print('train done')
###############################################################################################
#отчеты и результаты                                                                          #
###############################################################################################

def vec_for_learning(model, tagged_docs): 
    sents = tagged_docs
    targets, regressors = zip(*[(doc.tags[0], model.infer_vector(doc.words, steps=20)) for doc in sents])
    return targets, regressors


key_train, vec_train = vec_for_learning(model_dmm, tagget_train) # переменные = значения, список векторов для обучения
print('keys and vectors maked for train')

key_test, vec_test = vec_for_learning(model_dmm, tagget_test)    # переменные = значения, список векторов для тернировки
print('keys and vectors maked for test')

logreg = LogisticRegression(n_jobs=1, C=1e5)
logreg.fit(vec_train, key_train)
y_pred = logreg.predict(vec_test)

print('Testing accuracy %s' % accuracy_score(key_test, y_pred))
print('Testing F1 score: {}'.format(f1_score(key_test, y_pred, average='weighted')))


model_dmm.wv.save('./model/d2w.model2')

