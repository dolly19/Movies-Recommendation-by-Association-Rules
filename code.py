# -*- coding: utf-8 -*-
"""Copy of DMG2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_2oqT2FTpJbMQ6QzNQ9fSmA5mn57QBcX
"""

# Commented out IPython magic to ensure Python compatibility.
from google.colab import drive
drive.mount('/content/gdrive')
# %cd '/content/gdrive/MyDrive/ML datasets/ml-latest-small'
# %ls

import warnings
warnings.filterwarnings('ignore')

# Commented out IPython magic to ensure Python compatibility.
#install packages
!pip install dython
# %pip install mlxtend --upgrade
!pip install anytree

#importing libraries
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import association_rules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dython.nominal import associations
from dython.nominal import identify_nominal_columns
from mlxtend.frequent_patterns import fpmax
import itertools

"""#Question 1"""

#reading data
data_links = pd.read_csv("links.csv") 
data_movies = pd.read_csv("movies.csv") 
data_ratings = pd.read_csv("ratings.csv") 
data_tags = pd.read_csv("tags.csv")

#Exploratory data analysis (EDA)

def analysis(data):
  #Introductory details about data
  print("Introductory details: ")
  print(data.info())
  print("\n")

  #Statistical Insight:
  print("Statistical insight: ")
  print(data.describe(), "\n")

  #Finding Number of Nan values per column
  print("Number of Nan values per column:")
  print(data.isnull().sum(), "\n")

  #Plot Correlation Heatmap for all features
  print("Correlation Heatmap:")
  complete_correlation= associations(data, filename= 'correlation.png', figsize=(10,10))
  print("\n")

  #finding frequently occurring values in categorical features,
  print("Finding frequently occurring values in categorical features :")
  categorical_features=identify_nominal_columns(data)
  for x in categorical_features:
    print("5 most frequently occurring values in ", x, ": ")
    print(data[x].value_counts().head(), "\n")


#Exploratory data analysis (EDA) of all 4 datasets
print("\n Exploratory data analysis (EDA) of movies.csv \n")
analysis(data_movies)
print("\n Exploratory data analysis (EDA) of ratings.csv \n")
analysis(data_ratings)
print("\n Exploratory data analysis (EDA) of tags.csv \n")
analysis(data_tags)
print("\n Exploratory data analysis (EDA) of links.csv \n")
analysis(data_links)

"""#Question 2

#Data preprocessing
"""

#merging data_ratings and data_movies 
data = data_movies.merge(data_ratings, on = 'movieId',how = 'inner')
print(len(data.userId.unique())," users")

def preprocessing(data_given):
  #dropping unnecessary columns
  data_given= data_given.drop('rating',axis=1)
  data_given= data_given.drop('timestamp',axis=1)
  data_given= data_given.drop('genres',axis=1)

  #preprocessing the dataset to create a transactional list in which every row represent a user and their selected movies
  data_list = data_given.groupby(by = ["userId"])["title"].apply(list)
  data_list = data_list.reset_index()
  data_list = data_list["title"].tolist()
  #print(len(data_list))

  #data is converted into binary using transactionEncoder
  encoding = TransactionEncoder()
  encoded_data = encoding.fit(data_list).transform(data_list)
  train = pd.DataFrame(encoded_data, columns=encoding.columns_)
  return train

#preprocessing data
train = preprocessing(data)
print(train.shape)

"""#Generating frequent itemsets"""

#Fpgrowth metric
fpgrowth_itemsets = fpgrowth(train, min_support=0.092, use_colnames=True)
fpgrowth_itemsets['itemsets'].apply(lambda x: len(x)).value_counts()

"""#Applying Association Rules"""

#Applying Association Rules using metric="lift" and threshold=1
model = association_rules(fpgrowth_itemsets,metric="lift",min_threshold=1)
#including a column for length of movies in antecedents column
model['length'] = model["antecedents"].apply(lambda x: len(x))
#dropping unnecessary columns
model = model.drop(["antecedent support","consequent support", "leverage", "conviction"], axis=1)
print(model.shape)

model['antecedents'][4]

#Function to return list of K recommended movies based on a gievn movie_set
#K = no of movies to be recommended 
data_movies_copy = data_movies.copy(deep=True)

#Function to Recommend movies using association Rules:
def recommend(movie_set, K):
  recommended_movies_list=[]
  #rules only with given length
  result= model[model["length"].apply(lambda x: len(movie_set)==x)]
  #rules only containing given movies
  for movie in movie_set:
    result= result[result["antecedents"].apply(lambda x: movie in str(x))]
  #sort rules by lift

  if(len(result)!=0):
    result = result.sort_values(ascending=False,by='lift')
    result= result.reset_index()
    for index, row in result.iterrows():
      #print(row["consequents"])
      for movie in row["consequents"]:
        if recommended_movies_list.count(movie)==0: #to avoid recommending duplicate movies
          recommended_movies_list.append(str(movie))
        if len(recommended_movies_list)== K:
          break
      if len(recommended_movies_list)== K:
          break

  if len(recommended_movies_list)<K :
    rec_genre= recommend_by_genre(movie_set.pop())
    if len(rec_genre)==0:
      return recommended_movies_list
    for index, row in rec_genre.iterrows():
      if recommended_movies_list.count(str(row['title']))==0 and (str(row['title']) not in movie_set): #to avoid recommending duplicate movies
        recommended_movies_list.append(str(row['title']))
      if len(recommended_movies_list)== K:
        break

  return recommended_movies_list


#Function to recommend genres if association rules give 0 recommendations
def recommend_by_genre(movie_name):
  da = data_movies_copy.merge(data_ratings, on = 'movieId',how = 'inner')
  da.drop(columns=['userId','timestamp','movieId'],inplace=True)
  da = da.sort_values(ascending=False,by='rating')
  da.drop_duplicates(subset ="title", keep = 'first', inplace = True)
  temp = pd.DataFrame(columns = ['title','genres','rating'])
  for index, row in da.iterrows():
    gen = row['genres']
    final = set(map(str, gen.split('|')))
    da['genres'][index] = final
  row = da[da['title'] == movie_name]
  movie_genre = row['genres'].values
  movie_genre= movie_genre[0]
  for index, row in da.iterrows():
    s = row['genres']
    if s.issubset(movie_genre):
      temp = temp.append({'title' : da['title'][index] , 'genres' : da['genres'][index], 'rating' : da['rating'][index]}, ignore_index = True)
  temp['length'] = temp['genres'].apply(lambda x: len(x))
  temp = temp.sort_values(ascending=False,by=['rating','length'])
  temp.drop(temp.index[temp['title'] == movie_name], inplace=True)
  temp= temp.reset_index()
  return temp

#recommending movies 
movie_set= {"Forrest Gump (1994)", "Shawshank Redemption"}
res= recommend(movie_set, 4)
print("4 recommended movies are : ", res)

"""##Input Output:"""

# test_data= pd.read_csv('sample_test.tsv', sep='\t')

# predictions=[]
# for ind, row in test_data.iterrows():
#   movies_test = set(row['movies'].split("\n"))
#   recom= recommend(movies_test, 4)
#   predictions.append("\n".join(recom))


# output_data= []
# for i in range(len(predictions)):
#     output_data.append(predictions[i])
# output_df=pd.DataFrame(output_data,columns=['recommendation'])
# output_df.to_csv('output.csv', sep='\t', index=False)
# print("\n Output File: \n")
# print(output_df)
# print("\n\n\n")

"""#Question 3

"""

#fpmax() to find all maximal frequent pattern sets
maximal = fpmax(train, min_support=0.092, use_colnames=True)
maximal['itemsets'].apply(lambda x: len(x)).value_counts()

#Adding a column 'length' to include no of movies in maximal itemsets
maximal['length'] = maximal['itemsets'].apply(lambda x: len(x))

maximal

#Function to create FP-Tree based on given set of movies
'''This function will create FP-Tree visualization of the maximal frequent pattern set only for the movies given as input.
   MAXIMAL FREQUENT ITEMSETS will have Maximal Frequent Itemsets return before their name
   Try to give less than 20 movies, as FP-Tree can be very big. (2^d node)'''
def recursive(comb, parent):
  if len(comb)<1:
    return
  #create subsets(childs)
  sub= set(itertools.combinations(comb, len(comb)-1))
  for x in sub:
    #Check if subset if maximal Frequent
    if(in_maximal(x)):
      parent_x = Node("Maximal Frequent Itemset: "+" | ".join(x), parent=parent)
    else:
      parent_x = Node(" | ".join(x), parent=parent)
    recursive(x, parent_x)

#Function to check if the given itemset is present in MAXIMAL FREQUENT ITEMSETS
def in_maximal(movie_set):
  result= maximal[maximal["length"].apply(lambda x: len(movie_set)==x)]
  for movie in movie_set:
    if(len(result)!=0):
      result= result[result["itemsets"].apply(lambda x: movie in str(x))]
  if len(result)!=0:
    return True
  else:
    return False

#Set of movies to be given as input for FP- Tree visulaization of maximal itemsets

comb= {'Lord of the Rings: The Return of the King, The (2003)',
           'Spider-Man 2 (2004)',
           'Star Wars: Episode IV - A New Hope (1977)'}

#Visualize the maximal frequent pattern set.
if(in_maximal(comb)):
  ceo = Node("Maximal Frequent Itemset: "+" | ".join(comb)) #root
else:
  ceo = Node(" | ".join(comb))
recursive(comb, ceo)

#Store FP-TREE in png form.
DotExporter(ceo).to_picture("First.png")

# importing networkx
import networkx as nx
# importing matplotlib.pyplot
import matplotlib.pyplot as plt
 
maximal_2 = fpmax(train, min_support=0.092, use_colnames=True, max_len=2)
some_maximal= maximal_2.sample(n=10)
g = nx.DiGraph()

for index, row in some_maximal.iterrows():
  sr= row['itemsets']
  sub= "|".join(sr)
  for movie in sr:
    g.add_edge(sub, str(movie))

fig = plt.figure(1, figsize=(200, 60), dpi=10)
#nx.draw_networkx_labels(g, pos=nx.spring_layout(g), font_size=100, font_color='k', font_family='sans-serif', font_weight='normal')
nx.draw(g, with_labels = True, node_size=5000, font_size=100)