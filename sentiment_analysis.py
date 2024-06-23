#Import library yang dibutuhkan
import re, string, unicodedata #modul regular expression
import nltk
from nltk import word_tokenize, sent_tokenize #Paket ini membagi teks input menjadi kata-kata.,
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

#reading the dataset

df= pd.read_csv('/content/drive/MyDrive/dataset_prakerja.csv', header=0)
df.head(5)

df.info()

df['full_text']

df.columns

del(df["id_dataset"])
del(df["text_bersih"])
del(df["hasil_sentistrength"])
del(df['label_sentistrength'])
del(df['class'])

df

"""# 02 Text Preprocessing"""

! pip install swifter
! pip install Sastrawi

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
import nltk
import string
import re
import csv
import swifter
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

import nltk

print('Dataset size:',df.shape)
print

df.info()

string.punctuation

#CLEANING TEXT
def remove_punct(text):
    text = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",text)
    text = re.sub(r'^RT[\s]+', '', text)
    text = re.sub('/n', ' ',text)
    text = re.sub(r'((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text)
    text = re.sub(r' +', ' ',text)
    return text

df['FULL_TEXT'] = df['full_text'].apply(lambda x: remove_punct(x))
df.head(5)

#TOKENIZATION

def tokenization(text):
    text = re.split('\W+', text)
    return text

df['TOKENIZATION'] = df['full_text'].apply(lambda x: tokenization(x.lower()))
df.head(5)

#STOPREMOVAL
nltk.download('stopwords')
stopword = nltk.corpus.stopwords.words('indonesian')


def remove_stopwords(text):
    text = [word for word in text if word not in stopword]
    return text

df['STOP_REMOVAL'] = df['TOKENIZATION'].apply(lambda x: remove_stopwords(x))
df.head(5)

#CASE FOLDING
df['FULL_TEXT'] = df['full_text'].str.lower()
df.head(5)

df.head(5)

stop_removal = df[['STOP_REMOVAL']]

def fit_stopwords(text):
    text = np.array(text)
    text = ' '.join(text)
    return text

df['STOP_REMOVAL'] = df['STOP_REMOVAL'].apply(lambda x: fit_stopwords(x))

# WORD NORMALIZATION
# Download corpus kumpulan slangwords
! wget https://raw.githubusercontent.com/Shin865/analisis-sentiment/main/kamus_singkatan.csv

# berikut adalah kamus slang words dari Meisa Putri yang saya dapat di github
key_norm = pd.read_csv('kamus_singkatan.csv', sep=';', header=None)
key_norm.columns=['singkat','hasil']
print(key_norm.head())

key_norm.shape

# buat fungsi text normalize untuk mengubah kata singkat/kata tak baku menjadi kata baku
def text_normalize(text):
  text = ' '.join([key_norm[key_norm['singkat'] == word]['hasil'].values[0] if (key_norm['singkat'] == word).any() else word for word in text.split()])
  text = str.lower(text)
  return text

df['normalization'] = df['STOP_REMOVAL'].apply(lambda x: text_normalize(x))

#STEMMING
factory = StemmerFactory()
stemmer = factory.create_stemmer()

def stemming(text):
    return stemmer.stem(text)

df['STEMMING'] = df['normalization'].apply(lambda x: stemming(x))
df.head(5)

df = df['STEMMING']
df.head(5)

df.to_csv('HASIL3.csv', index = False)

"""# LEXICON MODEL"""

import pandas as pd
import numpy as np

# download kamus lexicon
! wget https://raw.githubusercontent.com/Shin865/analisis-sentiment/main/lexicon_negatif.csv
! wget https://raw.githubusercontent.com/Shin865/analisis-sentiment/main/lexicon_positif.csv

# Determine sentiment polarity of tweets using indonesia sentiment lexicon (source : https://github.com/fajri91/InSet)

# Loads lexicon positive and negative data
lexicon_positif = dict()
import csv
with open('lexicon_positif.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        lexicon_positif[row[0]] = int(row[1])

lexicon_negatif = dict()
import csv
with open('lexicon_negatif.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        lexicon_negatif[row[0]] = int(row[1])

# Function to determine sentiment polarity of tweets
def sentiment_analysis_lexicon_indonesia(text):
    #for word in text:
    score = 0
    for word in text:
        if (word in lexicon_positif):
            score = score + lexicon_positif[word]
    for word in text:
        if (word in lexicon_negatif):
            score = score + lexicon_negatif[word]
    polarity=''
    if (score > 0):
        polarity = 1
    elif (score < 0):
        polarity = -1
    else:
        polarity = 0
    return score, polarity

data = pd.read_csv('/content/HASIL3.csv')

data

import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize

data['STEMMING'] =pd.Series(data['STEMMING'],dtype="string")

data['STEMMING'] = data['STEMMING'].replace(np.nan, '')

data['tokenized_sents'] = data.apply(lambda row: word_tokenize(row['STEMMING']), axis=1)

data.info()

results = data['tokenized_sents'].apply(sentiment_analysis_lexicon_indonesia)
results = list(zip(*results))
data['polarity_score'] = results[0]
data['polarity'] = results[1]
print(data['polarity'].value_counts())

data

# Export to csv file
data.to_csv(r'data_label.csv', index = False, header = True,index_label=None)

data

"""# Wordcloud"""

from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
sns.set(style = 'whitegrid')

# load data berlabel
data = pd.read_csv('data_label.csv')

data

#define negative and positive
negatif = data.loc[data['polarity'] == -1]
positif  = data.loc[data['polarity'] == 1]
netral = data.loc[data['polarity'] == 0]

all_ = "".join(data.tokenized_sents.values) # untuk semua kata
all_negatif = "".join(negatif.tokenized_sents.values) # untuk kata negatif
all_positif = "".join(positif.tokenized_sents.values) # untuk kata positif
all_netral = "".join(netral.tokenized_sents.values) # untuk kata netral

# word cloud untuk semua kata
cloud = WordCloud(background_color = "white", max_words = 200, stopwords = set(STOPWORDS)).generate(all_)
fig, ax = plt.subplots(figsize = (5, 4))
ax.set_title('WordCloud Dataset Prakerja ', fontsize = 13)
ax.grid(False)
ax.imshow(cloud, interpolation='bilinear')
fig.tight_layout(pad=0)
ax.axis('off')
plt.show()

"""# PENGUJIAN SVM"""

! pip install Sastrawi

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import model_selection
from sklearn.model_selection import GridSearchCV, cross_val_score, KFold, ShuffleSplit
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import classification_report, confusion_matrix

data = pd.read_csv('data_label.csv', encoding='latin-1' )

data

data.describe()

data.isna().sum()

plt.hist(data.polarity)
plt.show()

data.polarity.value_counts()

df = data[['STEMMING','polarity']]
df.head()

from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split(df['STEMMING'],df['polarity'],
                                                                    test_size=0.2,random_state=0)
Encoder = LabelEncoder()
Train_Y = Encoder.fit_transform(Train_Y)
Test_Y = Encoder.fit_transform(Test_Y)
Tfidf_vect = TfidfVectorizer()
Tfidf_vect.fit(df['STEMMING'].values.astype('U'))
Train_X_Tfidf = Tfidf_vect.transform(Train_X.values.astype('U'))
Test_X_Tfidf = Tfidf_vect.transform(Test_X.values.astype('U'))

Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split(df['STEMMING'],df['polarity'],test_size=0.25, random_state=0)

Encoder = LabelEncoder()
Train_Y = Encoder.fit_transform(Train_Y)
Test_Y = Encoder.fit_transform(Test_Y)

Test_Y

"""<h1>TF-IDF</h1>"""

Train_X

Tfidf_vect = TfidfVectorizer()
Tfidf_vect.fit(df['STEMMING'].values.astype('U'))

Train_X_Tfidf = Tfidf_vect.transform(Train_X.values.astype('U'))
Test_X_Tfidf = Tfidf_vect.transform(Test_X.values.astype('U'))

Train_X_Tfidf.shape

Train_Y.shape

print("TF-IDF ", type(Test_X_Tfidf), Train_X_Tfidf.shape)

SVM = SVC()
cross_val_score(SVM,Train_X_Tfidf,Train_Y, cv=10)

cross_val_score(SVM,Train_X_Tfidf,Train_Y, cv=10).mean()

"""<h1>Membandingkan Kernel</h1>
<h2>1.Linear</h2>
"""

clf = SVC(kernel='linear', C=2.33)
clf.fit(Train_X_Tfidf,Train_Y)

scores = cross_val_score(clf, Train_X_Tfidf, Train_Y, cv=10)
print(scores)
print("K-Fold Mean -> ",cross_val_score(clf,Train_X_Tfidf,Train_Y, cv=10).mean())

y_pred = clf.predict(Test_X_Tfidf)

print(confusion_matrix(Test_Y, y_pred))
print("SVM Accuracy Score -> ",accuracy_score(y_pred, Test_Y)*100)
print("SVM Recall Score -> ",recall_score(y_pred, Test_Y, average='micro')*100)
print("SVM Precision Score -> ",precision_score(y_pred, Test_Y, average='micro')*100)
print("SVM f1 Score -> ",f1_score(y_pred, Test_Y, average='micro')*100)

"""<h2>2.Polynomial</h2>"""

poly = SVC(kernel='poly', C=2.33)
poly.fit(Train_X_Tfidf,Train_Y)

scores = cross_val_score(poly, Train_X_Tfidf, Train_Y, cv=10)
print(scores)
print("K-Fold Mean -> ",cross_val_score(poly,Train_X_Tfidf,Train_Y, cv=10).mean())

y_pred = poly.predict(Test_X_Tfidf)

print(confusion_matrix(Test_Y, y_pred))
print("SVM Accuracy Score -> ",accuracy_score(y_pred, Test_Y)*100)
print("SVM Recall Score -> ",recall_score(y_pred, Test_Y, average='micro')*100)
print("SVM Precision Score -> ",precision_score(y_pred, Test_Y, average='micro')*100)
print("SVM f1 Score -> ",f1_score(y_pred, Test_Y, average='micro')*100)

"""<h2>3.Radial Basis Function</h2>"""

rbf = SVC(kernel='rbf', C=2.13, gamma=0.50 )
rbf.fit(Train_X_Tfidf,Train_Y)

scores = cross_val_score(rbf, Train_X_Tfidf, Train_Y, cv=10)
print(scores)
print("K-Fold Mean -> ",cross_val_score(rbf,Train_X_Tfidf,Train_Y, cv=10).mean())

y_pred = rbf.predict(Test_X_Tfidf)

print(confusion_matrix(Test_Y, y_pred))
print("SVM Accuracy Score -> ",accuracy_score(y_pred, Test_Y)*100)
print("SVM Recall Score -> ",recall_score(y_pred, Test_Y, average='micro')*100)
print("SVM Precision Score -> ",precision_score(y_pred, Test_Y, average='micro')*100)
print("SVM f1 Score -> ",f1_score(y_pred, Test_Y, average='micro')*100)

"""<h2>4.Sigmoid</h2>"""

sig = SVC(kernel='sigmoid', C=2.25)
sig.fit(Train_X_Tfidf,Train_Y)

scores = cross_val_score(sig, Train_X_Tfidf, Train_Y, cv=10)
print(scores)
print("K-Fold Mean -> ",cross_val_score(sig,Train_X_Tfidf,Train_Y, cv=10).mean())

y_pred = sig.predict(Test_X_Tfidf)

print(confusion_matrix(Test_Y, y_pred))
print("SVM Accuracy Score -> ",accuracy_score(y_pred, Test_Y)*100)
print("SVM Recall Score -> ",recall_score(y_pred, Test_Y, average='micro')*100)
print("SVM Precision Score -> ",precision_score(y_pred, Test_Y, average='micro')*100)
print("SVM f1 Score -> ",f1_score(y_pred, Test_Y, average='micro')*100)

def classify(tweet):
    pred  = clf.predict(Tfidf_vect.transform([tweet]))
    if pred == 1:
        return "Sentimen positif"
    elif pred == -1:
        return "Sentimen negatif"
    else :
        return "Sentimen netral"

classify ('kartu prakerja nggak guna mending nganggur aja')

"""# Pengujian Naive Bayes

## 1. Gaussian Naive Bayes
"""

from sklearn.naive_bayes import GaussianNB

c = Train_X_Tfidf.toarray()

GNB = GaussianNB()
GNB.fit(c,Train_Y)

cv = ShuffleSplit(n_splits=10)

cv_accuracy = (cross_val_score(GNB,c,Train_Y, cv=cv, scoring='accuracy'))
avg_accuracy = np.mean(cv_accuracy)

print('Akurasi setiap split:', cv_accuracy, '\n')
print('Rata-rata akurasi pada cross validation:', avg_accuracy)

d = Test_X_Tfidf.toarray()

# Commented out IPython magic to ensure Python compatibility.
# %%time
# GNB_pred= GNB.predict(d)
# accuracy_GNB = accuracy_score(Test_Y, GNB_pred)
# print(accuracy_GNB)

# confusion Matrix
cm = confusion_matrix(Test_Y, GNB_pred)
print('Confusion matrix:\n', cm)
print('Classification report:\n', classification_report(Test_Y, GNB_pred))

print('micro Average :')
print("GaussianNB Recall Score -> ",recall_score(Test_Y, GNB_pred, average='micro')*100)
print("GaussianNB Precision Score -> ",precision_score(Test_Y, GNB_pred, average='micro')*100)
print("GaussianNB f1 Score -> ",f1_score(Test_Y, GNB_pred, average='micro')*100)

"""## Multinominal Naive Bayes"""

from sklearn.naive_bayes import MultinomialNB
MNB = MultinomialNB()
MNB.fit(Train_X_Tfidf,Train_Y)

cv = ShuffleSplit(n_splits=10)

cv_accuracy = (cross_val_score(MNB, Train_X_Tfidf,Train_Y, cv=cv, scoring='accuracy'))
avg_accuracy = np.mean(cv_accuracy)

print('Akurasi setiap split:', cv_accuracy, '\n')
print('Rata-rata akurasi pada cross validation:', avg_accuracy)

# Commented out IPython magic to ensure Python compatibility.
# %%time
# MNB_pred= MNB.predict(Test_X_Tfidf)
# accuracy_MNB = accuracy_score(Test_Y, MNB_pred)
# print(accuracy_MNB)

cm = confusion_matrix(Test_Y, MNB_pred)
print('Confusion matrix:\n', cm)
print('Classification report:\n', classification_report(Test_Y, MNB_pred))

print('micro Average :')
print("MultinominalNB Recall Score -> ",recall_score(Test_Y, MNB_pred, average='micro')*100)
print("MultinominalNB Precision Score -> ",precision_score(Test_Y, MNB_pred, average='micro')*100)
print("MultinominalNB f1 Score -> ",f1_score(Test_Y, MNB_pred, average='micro')*100)

"""## Bernoulli Naive Bayes"""

from sklearn.naive_bayes import BernoulliNB
BNB = BernoulliNB()
BNB.fit(Train_X_Tfidf,Train_Y)

cv = ShuffleSplit(n_splits=10)

cv_accuracy = (cross_val_score(BNB, Train_X_Tfidf,Train_Y, cv=cv, scoring='accuracy'))
avg_accuracy = np.mean(cv_accuracy)

print('Akurasi setiap split:', cv_accuracy, '\n')
print('Rata-rata akurasi pada cross validation:', avg_accuracy)

# Commented out IPython magic to ensure Python compatibility.
# %%time
# BNB_pred= BNB.predict(Test_X_Tfidf)
# accuracy_BNB = accuracy_score(Test_Y, BNB_pred)
# print(accuracy_BNB)

cm = confusion_matrix(Test_Y, BNB_pred)
print('Confusion matrix:\n', cm)

print('Classification report:\n', classification_report(Test_Y, BNB_pred))

print('micro Average :')
print("BernoulliNB Recall Score -> ",recall_score(Test_Y, BNB_pred, average='micro')*100)
print("BernoulliNB Precision Score -> ",precision_score(Test_Y, BNB_pred, average='micro')*100)
print("BernoulliNB f1 Score -> ",f1_score(Test_Y, BNB_pred, average='micro')*100)

print('Akurasi Naive Bayes :\n')
print('Gaussian Naive Bayes : ',accuracy_GNB )
print('Multinominal Naive Bayes : ',accuracy_MNB )
print('Bernoulli Naive Bayes : ',accuracy_BNB )

from sklearn.model_selection import GridSearchCV

# Define the parameter grid for hyperparameter tuning
param_grid = {
    'alpha': [0.001, 0.01, 0.1, 1, 10, 100],
    'fit_prior': [True, False],
}

# Create a GridSearchCV object
grid_search = GridSearchCV(MultinomialNB(), param_grid, cv=5)

# Fit the grid search object to the training data
grid_search.fit(Train_X_Tfidf, Train_Y)

# Print the best parameters
print("Best parameters:", grid_search.best_params_)

# Print the best model's accuracy
best_model = grid_search.best_estimator_
accuracy = best_model.score(Test_X_Tfidf, Test_Y)
print("Accuracy of the best model:", accuracy)

from sklearn.model_selection import KFold, cross_val_score

# Define the tuned Naive Bayes model
tuned_nb = MultinomialNB(alpha=0.1, fit_prior=True)

# Create a KFold object with 5 splits
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Perform cross-validation and store the accuracy scores
accuracy_scores = cross_val_score(tuned_nb, Train_X_Tfidf, Train_Y, cv=kf)

# Print the accuracy scores and standard deviation
print("Accuracy scores:", accuracy_scores)
print("Mean accuracy:", accuracy_scores.mean())
print("Standard deviation:", accuracy_scores.std())

# prompt: buatkan coding hyperparameter tuning untuk model SVC

from sklearn.model_selection import GridSearchCV

# Define the parameter grid for hyperparameter tuning
param_grid = {
    'C': [0.1, 0.5, 1, 10, 100],
    'gamma': [0.001, 0.01, 0.1, 1],
    'kernel': ['linear', 'poly', 'rbf', 'sigmoid']
}

# Create a GridSearchCV object
grid_search = GridSearchCV(SVC(), param_grid, cv=5)

# Fit the grid search object to the training data
grid_search.fit(Train_X_Tfidf, Train_Y)

# Print the best parameters
print("Best parameters:", grid_search.best_params_)

# Print the best model's accuracy
best_model = grid_search.best_estimator_
accuracy = best_model.score(Test_X_Tfidf, Test_Y)
print("Accuracy of the best model:", accuracy)

# prompt: buatkan coding Kfold sebanyak 5 kali untuk model SVC yang sudah di tuning, tunjukkan juga semua akurasinya dan juga standar deviasi

# Define the tuned SVC model
tuned_svm = SVC(C=10, gamma=0.1, kernel='rbf')

# Create a KFold object with 5 splits
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Perform cross-validation and store the accuracy scores
accuracy_scores = cross_val_score(tuned_svm, Train_X_Tfidf, Train_Y, cv=kf)

# Print the accuracy scores and standard deviation
print("Accuracy scores:", accuracy_scores)
print("Mean accuracy:", accuracy_scores.mean())
print("Standard deviation:", accuracy_scores.std())

# prompt: buatkan coding uji normalitas kedua model yang sudah di tuning

# Shapiro-Wilk test for tuned Naive Bayes model
from scipy.stats import shapiro

# Calculate the Shapiro-Wilk test statistic and p-value
stat, p = shapiro(accuracy_scores)

# Print the results
print("Shapiro-Wilk test for tuned Naive Bayes model:")
print("Statistic:", stat)
print("p-value:", p)

# Shapiro-Wilk test for tuned SVM model
from scipy.stats import shapiro

# Calculate the Shapiro-Wilk test statistic and p-value
stat, p = shapiro(accuracy_scores)

# Print the results
print("Shapiro-Wilk test for tuned SVM model:")
print("Statistic:", stat)
print("p-value:", p)
