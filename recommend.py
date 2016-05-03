import numpy as np
import pandas as pd
import requests
import time

import scipy.sparse as spp
from scipy.spatial import distance
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

import json
import math

from xml.etree import cElementTree as ET

class CONST(object):
    API_KEY = "AB0D4135B7DAF7A61E9BCC9903AD330A"
    DB_SOURCE = "./static/db.csv"
    def __setattr__(self, *_):
        pass

CONST = CONST()
    
def get_steamID64(url):
    url_elements = url.split("/")
    print url_elements
    if 'home' in url_elements:       
        url_elements.remove('home')
    url = '/'.join(url_elements)
    if url[-1] != '/':
        url += '/'
    url_string = url + '?xml=1'
    print url_string
    page = requests.get(url_string)
    page.raise_for_status()
    root = ET.fromstring(page.content)
    element = root.getchildren()[0]
    if element.tag == 'steamID64':
        return int(element.text)
    for ele in root.getchildren():
        if ele.tag == 'steamID64':
            return int(ele.text)
    return -1
    
    
def get_user_json(url):
    r = requests.get(url)
    if r.json()['response']['game_count'] == 0:
        print 'No games on the account'
        print 'To implement: cold start'
        raise Exception('No games')
    return r.json()

def get_user_data(url):
    temp = pd.DataFrame(get_user_json(url)['response']['games'])
    if 'playtime_2weeks' not in temp.columns:
        temp['playtime_2weeks'] = 0
    temp.columns = ['AppId','playtime_2weeks','playtime_forever']
    return temp

def weight(t_f,t_w):
    return weight_lowend_bias(t_f,t_w)

def weight_lowend_bias(t_f,t_w):
    return (1.0+2.0*math.log(t_f+1.0,2.0))*(1.0+0.5*math.log(t_w+1.0,8.0))

def weight_highend_bias(t_f,t_w):
    return (1.0+6.0*math.log(t_f+1.0,2.0))*(1.0+0.16*math.log(t_w+1.0,64.0))

def generate_weights_dict(df):
    weights = {}
    for i,row in df.iterrows():
        #print type(row)
        t_w = row['playtime_2weeks']/60.0
        t_f = row['playtime_forever']/60.0
        weights[row['appid']] = weight(t_f,t_w)
    return weights

def generate_weights(df,remove_columns=False):
    df['Weight'] = 0.0
    for i,row in df.iterrows():
        #print type(row)
        t_w = row['playtime_2weeks']/60.0
        t_f = row['playtime_forever']/60.0
        df.set_value(i,'Weight',weight(t_f,t_w))
    if remove_columns:
        df.drop(['playtime_2weeks'],axis=1,inplace=True)
        df.drop(['playtime_forever'],axis=1,inplace=True)
    return weight

def read_database(file=CONST.DB_SOURCE):
    return pd.read_csv(file)

def misval(df,columns=[],categorical=False):
    if categorical:
        for col in columns:
            df[col].fillna("",inplace=True)
    else:
        for col in columns:
            df[col].fillna(0,inplace=True)

def one_hot_encoding(df,columns=[],sep="*"):
    for col in columns:
        df = df.join(pd.Series(df[col]).str.get_dummies(sep=sep))
        df.drop([col],axis=1,inplace=True)
    return df

# @param: uid as numeric
# @return: list of tuples: ( appid(owned_game), name(owned_game), appid(predicted_game), name(predicted_game) )
def recommend(uid):
    # -->Setting up & Preprocessing Data<--
    # load sqlserver data
    db = read_database()
    # clean up / preprocess server data (Note: perhaps implement data cleaning upon storage into server)
    misval(db,columns=['Developer','Publisher','Description'],categorical=True)
    db = one_hot_encoding(db,columns=['Genre','Tag'],sep="*")
    db = pd.get_dummies(db,columns=['Developer','Publisher'])
    # load user data
    access_string = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key='+CONST.API_KEY+'&steamid='+str(uid)+'&format=json&include_played_free_games=true'
    user_data = get_user_data(access_string)
    # generate weights column + remove playtime columns
    misval(user_data,columns=['playtime_2weeks','playtime_forever'],categorical=False)
    generate_weights(user_data,remove_columns=True)
    # sort list by weights + remove weight column
    user_data.sort_values('Weight',axis=0,ascending=False, inplace=True, kind='quicksort', na_position='last')
    user_data.drop(['Weight'],axis=1,inplace=True)
    # merge user_data with db
    user_data = pd.merge(user_data, db, how='inner', on=['AppId'])
    # create dictionary of owned games
    owned_games = set(user_data['AppId'].to_dict().values())
    if len(user_data.index) > 10:
        user_data = user_data.iloc[0:10]
    # Tf-idf word processing
    
#   Column Weighting
    for col in db.columns:
        if 'Tag' in col:
            db[col] *= 2
    
#     db['TagSandbox'] *= 2.5
    
    for col in user_data.columns:
        if 'Tag' in col:
            user_data[col] *= 2
    
#     user_data['TagSandbox'] *= 2.5
                    
    desc_vector = TfidfVectorizer(analyzer='word', ngram_range=(1,1), stop_words = 'english')
    db_word_matrix = desc_vector.fit_transform(db['Description'])
    user_word_matrix = desc_vector.transform(user_data['Description'])
    
    title_vector = TfidfVectorizer(analyzer='word', ngram_range={1,2}, stop_words = 'english')
    db_title_matrix = title_vector.fit_transform(db['Title'])
    user_title_matrix = title_vector.transform(user_data['Title'])

    # Temp Drop
    db.drop(['Owners'],axis=1,inplace=True)
    user_data.drop(['Owners'],axis=1,inplace=True)

    # Convert Data to sparse matrices and hstack with Tfidf features
    db_num = db._get_numeric_data().as_matrix()
    user_num = user_data._get_numeric_data().as_matrix()
    
    x_data = db_num[ : , 1: ]
    y_data = user_num[ : , 1: ]

    x_data_sparse = spp.csr_matrix(x_data)
    y_data_sparse = spp.csr_matrix(y_data)

    x_data_final = spp.hstack([x_data_sparse,db_word_matrix,db_title_matrix])
    y_data_final = spp.hstack([y_data_sparse,user_word_matrix,user_title_matrix])
    
    # -->Analyzing Data<--
    
    nbrs = NearestNeighbors(n_neighbors=40, algorithm='brute',metric='euclidean').fit(x_data_final)
    distances, indices = nbrs.kneighbors(y_data_final)
    chosen = []
    chosen_list = []
    for i in xrange(indices.shape[0]):
        n_iter = 0
        start_member = db.iloc[indices[i,0]]
        chosen_member = db.iloc[indices[i,1]]
        while chosen_member['AppId'] in owned_games or chosen_member['AppId'] in chosen_list:
            n_iter += 1
            chosen_member = db.iloc[indices[i,n_iter]]

        chosen_list.append(chosen_member['AppId'])
        chosen.append((start_member['AppId'],start_member['Title'],chosen_member['AppId'],chosen_member['Title']))
    return chosen

def runScript():
    # example usage
    url = raw_input('url: ')
    uid_test = get_steamID64(url)
    print "<<PROCESSING UID>>"
    start_time = time.time()
    for row in recommend(uid_test):
        print row
    print "Elapsed time: " + str(time.time()-start_time)
    print "------------------"

    # or for a list of uids
    uid_list = (76561198040715074,76561198048971211,76561198049109177,76561198039551867,76561198058290543) # Cameron, Aaron (derpking7), TJ (thunderwaffle), <random_friend> (TheWeedHead), Mark (Solari985)
    for uid in uid_list:
        print "<<PROCESSING UID>>"
        start_time = time.time()
        for row in recommend(uid):
            print row
        print "Elapsed time: " + str(time.time()-start_time)
        print "------------------"

#runScript()

