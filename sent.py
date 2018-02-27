import pymorphy2
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
import pandas as pd
import re
import csv


pos_arr = []
neg_arr = []
neu_arr = []
pp_arr = []
pn_arr = []
arr = []
file = pd.read_csv('/root/GolosProject/russian.csv')
file1 = pd.read_csv('/root/GolosProject/phrases.csv')
arr.append(set(file['word']))
for i in range(len(file['score'])):
    if file['score'][i] == 1.7 or file['score'][i] == -1.7:
        neu_arr.append(file['word'][i])
    if file['score'][i] < -1.7:
        neg_arr.append(file['word'][i])
    if file['score'][i] > 1.7:
        pos_arr.append(file['word'][i])
for i in range(len(file1['tone'])):
    if file1['tone'][i] == 'pos':
        pp_arr.append(file1['word'][i])
    if file1['tone'][i] == 'neg':
        pn_arr.append(file1['word'][i])  


def word_feats(words):
    w = words.split()
    return dict([(word, True) for word in w])
def neg_feats(words):
    w = words.split()
    return dict([(word, True) for word in w])
def neu_feats(words):
    w = words.split()
    return dict([(word, True) for word in w])
 
pos_features = [(word_feats(pos), 'pos') for pos in pos_arr]
neg_features = [(neg_feats(neg), 'neg') for neg in neg_arr]
neu_features = [(neu_feats(neu), 'neu') for neu in neu_arr]

train_set = pos_features + neg_features + neu_features
classifier = NaiveBayesClassifier.train(train_set)


def foo(sentence):
    f = open('unk.csv','a')
    writer = csv.writer(f)
    unk = []
    morph = pymorphy2.MorphAnalyzer()
    neg = 0
    pos = 0
    neu = 0
    sentence = sentence.lower()
    r = re.sub(r'\.','',str(sentence))
    r1 = re.sub(r',','',str(r))
    r2 = re.sub(r'!','',str(r1))
    r3 = re.sub(r'\?','',str(r2))
    for i in range(len(pp_arr)):
        if r3.find(pp_arr[i]) != -1:
            r3 = r3.replace(pp_arr[i],'')
            pos += 1
    for i in range(len(pn_arr)):
        if r3.find(pn_arr[i]) != -1:
            r3 = r3.replace(pn_arr[i],'')
            neg += 1
    words = r3.split(' ')
    for word in words:
        p = morph.parse(word)[0]
        if p.normal_form in arr[0]:
            classResult = classifier.classify(word_feats(p.normal_form))
            if classResult == 'neg':
                neg += 1
            if classResult == 'pos':
                pos += 1
            if classResult == 'neu':
                neu += 1
        else:
            unk.append(word)
    a = float(pos)/len(words)
    b = float(neg)/len(words)
    c = float(neu)/len(words)
    
    if b == a == c == 0:
        return 'Undefined:('
        for w in unk:
            writer.writerow([w,'unk'])
    elif c > a and c > b or a == b:
        return 'Neutral'
        for w in unk:
            writer.writerow([w,'neu'])
    elif a > b:
        return 'Positive'
        for w in unk:
            writer.writerow([w,'pos'])
    elif b > a:
        return 'Negative'
        for w in unk:
            writer.writerow([w,'neg'])
   
    
    print('Positive: ' + str(pos))
    print('Negative: ' + str(neg))
    print('Neutral: ' + str(neu))
