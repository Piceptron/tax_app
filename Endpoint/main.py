
from flask import Flask, jsonify, make_response, request
import MySQLdb

deductionPercentage = {"food": 0.5, "computers": 0.55, "furnature":0.2, "taxi":0.4, "other":1}

CURRENT_USER_ID = str(0)

DEFAULT_RATING = 70

INSTANCE_NAME = 'spatial-genius-232603:northamerica-northeast1:rec-sql'
DB_NAME = 'product_recs'
DB_USER = 'firstUser'
DB_PASS = '0'
# what if fetchall is null?
app = Flask(__name__)

def getCursor():
  # Connect to your DB
  db = MySQLdb.connect(unix_socket='/cloudsql/' + INSTANCE_NAME, db=DB_NAME, user=DB_USER, passwd=DB_PASS, charset='utf8')
  return db.cursor()

@app.route('/predict/getRecommendations', methods=['GET'])
def getRecommendation():
  # Fetch the recommendations
  cursor = getCursor()
  cursor.execute('SELECT userId FROM CurrentUser WHERE id = ' + CURRENT_USER_ID)
  print("Here Result:")
  userId = cgi.escape(cursor.fetchall()[0][0])
  print("Here Result:", userId)
  cursor.execute('SELECT title, category, price, tax r.prediction \
      FROM Product a \
      INNER JOIN Recommendation r \
      ON r.productId = a.id \
      WHERE r.userId = ' + userId + ' \
      ORDER BY r.prediction desc')
  print("Here4")
  recommendations = []
  for acc in cursor.fetchall():
    percentSavings = deductionPercentage[cgi.escape(acc[1])]
    price = cgi.escape(acc[2])
    # Tax on deductable is returnable as tax credits.
    # Ideally as we have more data, we would tell them
    # you have used all your possible deductables
    # and cannot further save more (if total deductables
    # is greater than or equal to income) So eventually keep track of total
    tax = cgi.escape(acc[3])
    total = price + tax
    recommendations.append({
        'title': cgi.escape(acc[0]),
        'price': price,
        'tax': tax,
        "total": total,
        "discount" : deductionPercentage,
        "netTotal": total * (1 - deductionPercentage),
      })
  return make_response(jsonify(recommendations))

@app.route('/predict/login', methods=['POST'])
def login():
  content = request.json
  cursor = getCursor()
  cursor.execute('SET IDENTITY_INSERT CurrentUser ON; INSERT INTO  CurrentUser VALUES (0, ' + content["username"] + ')')
  # should we return a response?

@app.route('/predict/signup', methods=['POST'])
def signup():
  content = request.json
  cursor = getCursor()
  cursor.execute('INSERT INTO User VALUES (' + content["firstName"]  + ', '
                                            + content["lastName"]  + ', '
                                            + content["username"]  + ', '
                                            + content["email"]  + ', '
                                            + content["income"]  + ')')
  cursor.execute('SELECT MAX(id) FROM User')
  lastId = cgi.escape(cursor.fetchall()[0][0])
  cursor.execute('SET IDENTITY_INSERT CurrentUser ON; INSERT INTO  CurrentUser VALUES (0, ' + content["username"] + ')')


@app.route('/predict/addReceipt', methods=['POST'])
def generateNewRecommendation():
  content = request.json
  productId = 0 # Tim makes python function to get the product Id here
  cursor = getCursor()
  cursor.execute('SELECT userId FROM CurrentUser WHERE id = ' + CURRENT_USER_ID)
  userId = cgi.escape(cursor.fetchall()[0][0])
  cursor.execute('INSERT INTO Receipt VALUES (' + productId  + ', '
                                            + userId  + ', '
                                            + content["price"]  + ', '
                                            + content["tax"] + ')')
  # Can be imporved a lot instead of making default 70, if they previously hated it but bought it, what does that imply?
  # We can increase their rating by a bit?
  cursor.execute('SET IDENTITY_INSERT Rating ON; INSERT INTO  Rating VALUES (' + productId + ', ' + userId + ', ' + DEFAULT_RATING + ')')

if __name__ == '__main__':
    app.run(debug=True)