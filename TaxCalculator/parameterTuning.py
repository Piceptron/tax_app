import sys
import itertools
from math import sqrt
from operator import add
from os.path import join, isfile, dirname
from pyspark import SparkContext, SparkConf, SQLContext
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating

# Finds the most optimal parameters

USER_ID = 0

CLOUDSQL_INSTANCE_IP = sys.argv[1]
CLOUDSQL_DB_NAME = sys.argv[2]
CLOUDSQL_USER = sys.argv[3]
CLOUDSQL_PASSWORD  = sys.argv[4]

conf = SparkConf().setAppName("app_collaborative")
sc = SparkContext(conf=conf)
sqlContext = SQLContext(sc)

jdbcUrl = 'jdbc:mysql://%s:3306/%s?user=%s&password=%s' % (CLOUDSQL_INSTANCE_IP, CLOUDSQL_DB_NAME, CLOUDSQL_USER, CLOUDSQL_PASSWORD)

#[START how_far]
def howFarAreWe(model, against, sizeAgainst):
  # Ignore the rating column  
  againstNoRatings = against.map(lambda x: (int(x[0]), int(x[1])) )

  # Keep the rating to compare against
  againstWiRatings = against.map(lambda x: ((int(x[0]),int(x[1])), int(x[2])) )

  # Make a prediction and map it for later comparison
  # The map has to be ((user,product), rating) not ((product,user), rating)
  predictions = model.predictAll(againstNoRatings).map(lambda p: ( (p[0],p[1]), p[2]) )

  # Returns the pairs (prediction, rating)
  predictionsAndRatings = predictions.join(againstWiRatings).values()

  # Returns the variance
  return sqrt(predictionsAndRatings.map(lambda s: (s[0] - s[1]) ** 2).reduce(add) / float(sizeAgainst))
#[END how_far]

# Read the data from the Cloud SQL
# Create dataframes
dfRates = sqlContext.read.jdbc(url=jdbcUrl, table='Rating')
# rddUserRatings is actually always subset of training data somehow, even without inserting
# rddUserRatings into training data.
rddUserRatings = dfRates.filter(dfRates.userId == USER_ID).rdd
print(rddUserRatings.count())

# Split the data in 3 different sets : training, validating, testing
# 60% 20% 20%
rddRates = dfRates.rdd
rddTraining, rddValidating, rddTesting = rddRates.randomSplit([6,2,2])

#Add user ratings in the training model
print("Before: ", rddTraining.count())
rddTraining.union(rddUserRatings)
print("After: ", rddTraining.count())
nbValidating = rddValidating.count()

print("Training: %d, validation: %d, test: %d" % (rddTraining.count(), nbValidating, rddTesting.count()))

# Best results are not commented
ranks  = [5, 10,15]
reguls = [0.1, 1, 2]
iters  = [5,10, 15]

finalModel = None
finalRank  = 0
finalRegul = float(0)
finalIter  = -1
finalDist   = float(100)

#[START train_model]
for cRank, cRegul, cIter in itertools.product(ranks, reguls, iters):
  model = ALS.train(rddTraining, cRank, cIter, float(cRegul))
  dist = howFarAreWe(model, rddValidating, nbValidating)
  if dist < finalDist:
    print("Best so far:%f" % dist)
    finalModel = model
    finalRank  = cRank
    finalRegul = cRegul
    finalIter  = cIter
    finalDist  = dist
#[END train_model]

print("Rank %i" % finalRank)
print("Regul %f" % finalRegul) 
print("Iter %i" % finalIter)  
print("Dist %f" % finalDist) 
