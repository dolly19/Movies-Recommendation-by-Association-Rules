# Movies-Recommendation-by-Association-Rules
A movie recommendation model using the association rule mining techniques on movielens dataset. It was a assignment under the course Data Mining @IIITD.

## STEPS TO BUILD THE MODEL

1. Performed Exploratory data analysis (EDA) over the dataset.(Can read the documnetation for better understanding of data)

2. Merging data_ratings and data_movies

**Reason** - As Movies rating data contain more number of users as compared to tags data. Thus, it can be useful to be merged with the movie's title dataset to get more numbers of frequent items set implies with more number of rules and better recommendation.

3. Dropping unnecessary columns like ratings, timestamp, genres to get a more clear view

4. Preprocessing the dataset to create a transactional list in which every row represent a user and their selected movies (users count 610)

5. Encoding of data into binary using transactionEncoder

6. Generating frequent itemsets using FPGrowth metric

**Assumption**- parameters min_support = 0.092 , max_len = None

7. Applying association rule (number of rules generated around 96 lakhs)

**Assumption**- using Lift for making rules, threshold set = 1

8. Recommending k movies based on the top lift values

**Reason** - the increasing value of lift is relatively proportional to other measures also
such as confidence, support.

**Assumption**: For some movies, we don’t have any recommendations as there are no rules generated for them because of less frequency, it is removed from association rules and frequent item formation. So for considering those cases we are using movies genres and ratings from the dataset to recommend movies.

Team Member - Vidhi Sharma



