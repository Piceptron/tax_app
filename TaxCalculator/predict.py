from __future__ import print_function

import sys
import itertools
from math import sqrt
from operator import add
from os.path import join, isfile, dirname
from pyspark import SparkContext, SparkConf, SQLContext
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating
from pyspark.sql.types import StructType
from pyspark.sql.types import StructField
from pyspark.sql.types import StringType
from pyspark.sql.types import FloatType

conf = SparkConf().setAppName("app_collaborative")
sc = SparkContext(conf=conf)
sc.setCheckpointDir('checkpoint/')
sqlContext = SQLContext(sc)
# should check if empty (either user has no data, or user has all data filled)
USER_ID = 33

CLOUDSQL_INSTANCE_IP = sys.argv[1]
CLOUDSQL_DB_NAME = sys.argv[2]
CLOUDSQL_USER = sys.argv[3]
CLOUDSQL_PASSWORD  = sys.argv[4]

# BEST_RANK = int(sys.argv[5])
# BEST_ITERATION = int(sys.argv[6])
# BEST_REGULATION = float(sys.argv[7])

BEST_RANK = 10
BEST_ITERATION = 10
BEST_REGULATION = 1.0

TABLE_PRODUCTS  = "Product"
TABLE_RATINGS = "Rating"
TABLE_RECOMMENDATIONS = "Recommendation"

# Read the data from the Cloud SQL
# Create dataframes
#[START read_from_sql]
jdbcUrl = 'jdbc:mysql://%s:3306/%s?user=%s&password=%s' % (CLOUDSQL_INSTANCE_IP, CLOUDSQL_DB_NAME, CLOUDSQL_USER, CLOUDSQL_PASSWORD)
dfProducts = sqlContext.read.jdbc(url=jdbcUrl, table=TABLE_PRODUCTS)
dfRates = sqlContext.read.jdbc(url=jdbcUrl, table=TABLE_RATINGS)
#[END read_from_sql]

# Get all the ratings rows of our user
print(dfRates.count())
dfUserRatings  = dfRates.filter(dfRates.userId == USER_ID).rdd.map(lambda r: r.productId).collect()
print(dfUserRatings)

# Returns only the products that have not been rated by our user
rddPotential  = dfProducts.rdd.filter(lambda x: x[0] not in dfUserRatings)
pairsPotential = rddPotential.map(lambda x: (USER_ID, x[0]))
print(pairsPotential.count())

#[START split_sets]
rddTraining, rddValidating, rddTesting = dfRates.rdd.randomSplit([6,2,2])
print("Training: %d, validation: %d, test: %d" % (rddTraining.count(), rddValidating.count(), rddTesting.count()))
#[END split_sets]

#[START predict]
# Build our model with the best found values
# Rating, Rank, Iteration, Regulation
model = ALS.train(rddTraining, BEST_RANK, BEST_ITERATION, BEST_REGULATION)

# Calculate all predictions
# userId  productId  prediction
predictions = model.predictAll(pairsPotential).map(lambda p: (str(p[0]), str(p[1]), float(p[2])))

# Take the top 3 predictions
topPredictions = predictions.takeOrdered(3, key=lambda x: -x[2]) # To order from smallest?
print(topPredictions)

schema = StructType([StructField("userId", StringType(), True), StructField("productId", StringType(), True), StructField("prediction", FloatType(), True)])

#[START save_top]
dfToSave = sqlContext.createDataFrame(topPredictions, schema)
dfToSave.write.jdbc(url=jdbcUrl, table=TABLE_RECOMMENDATIONS, mode='overwrite')
#[END save_top]