from flask import Flask, request, json
from database import Example
from database import db
from database import createDatabase
import redis


app = Flask(__name__)


@app.route('/v1/expenses/', methods=['POST'])
def createEntry():
    try:
        session = createDatabase()
        db.create_all()
        ox = request.get_json(force=True)
        newUser = Example(ox['name'], ox['email'], ox['category'],ox['description'],
                      ox['link'], ox['estimated_costs'], ox['submit_date'],
                      'pending', '')

        db.session.add(newUser)
        db.session.flush()
        db.session.commit()

    except Exception as e:
        print e
        return json.dumps([{'Error Message':'Something went wrong on the server side.'}]), 400

    return json.dumps([{'id': newUser.id, 'name': newUser.name, 'email': newUser.email,
                        'category': newUser.category, 'description': newUser.description,
                        'link': newUser.link, 'estimated_costs': newUser.estimated_costs,
                        'submit_date': newUser.submit_date, 'status': newUser.status,
                        'decision_date': newUser.decision_date}]), 201

@app.route('/v1/expenses/<int:expense_id>', methods=['GET', 'PUT', 'DELETE'])
def withExpenseID(expense_id):
    ox2 = Example.query.filter_by(id=expense_id).first_or_404()

    if(request.method == 'DELETE'):
        db.session.delete(ox2)
        db.session.commit()
        return json.dumps([{'status':True}]), 204

    if(request.method == 'PUT'):
        ox3 = request.get_json(force=True)
        ox2.estimated_costs = ox3['estimated_costs']
        db.session.commit()
        return json.dumps([{'status':True}]), 202

    if (request.method == 'GET'):
        return json.dumps([{'id': ox2.id, 'name': ox2.name, 'email': ox2.email,
                        'category': ox2.category, 'description': ox2.description,
                        'link': ox2.link, 'estimated_costs': ox2.estimated_costs,
                        'submit_date': ox2.submit_date, 'status': ox2.status,
                        'decision_date': ox2.decision_date}])


if __name__ == '__main__':

    r_server = redis.Redis("127.0.0.1")
    r_server.lrem("FINAL", "5003", 0)
    r_server.rpush("FINAL", "5003")
    app.run(host="127.0.0.1", port=5003, debug=False)