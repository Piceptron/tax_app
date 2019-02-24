import cgi
import webapp2
import logging
import json

import MySQLdb

# Define your production Cloud SQL instance information.
_INSTANCE_NAME = 'spatial-genius-232603:cluster-5e33-m'
_DB_NAME = 'rec-sql'
_DB_USER = 'firstUser'
_DB_PASS = '0'
_USER_ID = str(0)


# Returns a list of the accommodation that the user already rated
class GetRatedHandler(webapp2.RequestHandler):
  print("called")
  def post(self):
    # Connect to your DB
    db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db=_DB_NAME, user=_DB_USER, passwd=_DB_PASS, charset='utf8')

    # Fetch the recommendations
    cursor = db.cursor()
    cursor.execute('SELECT  a.id, a.title, a.type, r.rating \
      FROM Rating r \
      INNER JOIN Accommodation a \
      ON r.accoId = a.id \
      WHERE userId = ' + _USER_ID)

    rated = []
    for r in cursor.fetchall():
      rated.append({
        'id': cgi.escape(r[0]),
        'title': cgi.escape(r[1]),
        'type': cgi.escape(r[2]),
        'rating': r[3]
      })

    json_response = json.dumps({
      'rated': rated
    })

    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json_response)

  def get(self):
    self.get()


# Returns a list of the recommendations for the user previously recorded by the recommendation engine
class GetRecommendationHandler(webapp2.RequestHandler):
  print("called")
  def post(self):
    # Connect to your DB
    db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db=_DB_NAME, user=_DB_USER, passwd=_DB_PASS, charset='utf8')

    # Fetch the recommendations
    cursor = db.cursor()
    cursor.execute('SELECT id, title, type, r.prediction \
      FROM Accommodation a \
      INNER JOIN Recommendation r \
      ON r.accoId = a.id \
      WHERE r.userId = ' + _USER_ID + ' \
      ORDER BY r.prediction desc')

    recommendations = []
    for acc in cursor.fetchall():
      recommendations.append({
        'id': cgi.escape(acc[0]),
        'title': cgi.escape(acc[1]),
        'type': cgi.escape(acc[2])
      })


    json_response = json.dumps({
      'recommendations': recommendations
    })

    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json_response)

  def get(self):
    self.post()

api = webapp2.WSGIApplication([
    ('/api/get_recommendations', GetRecommendationHandler),
    ('/api/get_rated', GetRatedHandler)
  ],
  debug=True
)