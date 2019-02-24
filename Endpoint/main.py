
from flask import Flask, jsonify, make_response, request
import MySQLdb

idMap = {"4":25, "22.58": 28, "Safeway":20}

deductionPercentage = {"food": 0.5, "computers": 0.55, "furnature":0.2, "taxi":0.4, "other":1}

CURRENT_USER_ID = str(0)

DEFAULT_RATING = 70

INSTANCE_NAME = 'spatial-genius-232603:northamerica-northeast1:rec-sql'
DB_NAME = 'product_recs'
DB_USER = 'firstUser'
DB_PASS = '0'
# what if fetchall is null?
app = Flask(__name__)

def getDB():
  # Connect to your DB
  db = MySQLdb.connect(unix_socket='/cloudsql/' + INSTANCE_NAME, db=DB_NAME, user=DB_USER, passwd=DB_PASS, charset='utf8')
  return db

def cursorOutput(fetchall):
  return [[b for b in a] for a in fetchall]

@app.route('/predict/getRecommendations', methods=['GET'])
def getRecommendation():
  # Fetch the recommendations
  db = getDB()
  cursor = db.cursor()
  cursor.execute('SELECT username FROM CurrentUser WHERE id = ' + CURRENT_USER_ID)
  username = cursorOutput(cursor.fetchall())[0][0]
  print("Here Result:", username)
  print('SELECT id FROM User WHERE username = \'' + username + '\'')
  cursor.execute('SELECT id FROM User WHERE username = \'' + username + '\'')
  userId = cursorOutput(cursor.fetchall())[0][0]
  print("Here Result:", userId)
  cursor.execute('SELECT title, category, price, tax, r.prediction \
      FROM Product a \
      INNER JOIN Recommendation r \
      ON r.productId = a.id \
      WHERE r.userId = ' + userId + ' \
      ORDER BY r.prediction desc')
  print("Here4")
  recommendations = []
  for acc in cursor.fetchall():
    acc = [x for x in acc]
    percentSavings = deductionPercentage[acc[1]]
    price = acc[2]
    # Tax on deductable is returnable as tax credits.
    # Ideally as we have more data, we would tell them
    # you have used all your possible deductables
    # and cannot further save more (if total deductables
    # is greater than or equal to income) So eventually keep track of total
    tax = acc[3]
    total = price + tax
    recommendations.append({
        'title': acc[0],
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
  db = getDB()
  cursor = db.cursor()
  print('INSERT INTO CurrentUser (id, username) VALUES (0, \'' + content["username"] + '\') ON DUPLICATE KEY UPDATE id = 0, username = \'' + content["username"] + '\'')
  cursor.execute('INSERT INTO CurrentUser (id, username) VALUES (0, \'' + content["username"] + '\') ON DUPLICATE KEY UPDATE id = 0, username = \'' + content["username"] + '\'')
  db.commit()
  return "success"

@app.route('/predict/signup', methods=['POST'])
def signup():
  print(request.json)
  content = request.json
  db = getDB()
  cursor = db.cursor()
  cursor.execute('SELECT MAX(id) FROM User')
  newId = int(cursorOutput(cursor.fetchall())[0][0]) + 1
  print(newId)
  cursor.execute('INSERT INTO User VALUES (' + newId + ', '
                                             + content["firstName"]  + ', '
                                            + content["lastName"]  + ', '
                                            + content["username"]  + ', '
                                            + content["email"]  + ', '
                                            + str(content["income"])  + ')')
  cursor.execute('INSERT INTO CurrentUser (id, username) VALUES (0, \'' + content["username"] + '\') ON DUPLICATE KEY UPDATE id = 0, username = \'' + content["username"] + '\'')
  db.commit()
  return "success"

@app.route('/predict/addReceipt', methods=['POST'])
def addReceipt():
  content = request.json
  productId =idMap[content["totalPrice"]] # idKey Tim makes python function to get the product Id here
  db = getDB()
  cursor = db.cursor()
  cursor.execute('SELECT userId FROM CurrentUser WHERE id = ' + CURRENT_USER_ID)
  userId = cursorOutput(cursor.fetchall())[0][0]
  cursor.execute('SELECT MAX(id) FROM Receipt')
  newId = int(cursorOutput(cursor.fetchall())[0][0]) + 1
  cursor.execute('INSERT INTO Receipt VALUES (' + newId + ', '
                                            + productId  + ', '
                                            + userId  + ', '
                                            + content["totalPrice"] - content["tax"],
                                            + content["tax"] + ')')
  # Can be imporved a lot instead of making default 70, if they previously hated it but bought it, what does that imply?
  # We can increase their rating by a bit?
  cursor.execute('SET IDENTITY_INSERT Rating ON; INSERT INTO  Rating VALUES (' + productId + ', ' + userId + ', ' + DEFAULT_RATING + ')')
  return "success"

if __name__ == '__main__':
    app.run(debug=True)