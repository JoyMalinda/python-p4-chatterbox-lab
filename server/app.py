from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import asc

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():

    if request.method == 'GET':
        mess_dict = [message.to_dict() for message in Message.query.order_by(asc(Message.created_at)).all()]
        response = make_response(
            jsonify(mess_dict),
            200
        )
        return response
    
    elif request.method == 'POST':
        data = request.get_json()
        username = data.get("username")
        body = data.get("body")

        if not username or not body:
            return make_response(jsonify({"error": "Username and body are required."}), 400)

        new_message = Message(username=username, body=body)
        db.session.add(new_message)
        db.session.commit()

        return make_response(jsonify(new_message.to_dict()), 201)


@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter(Message.id==id).first()

    if message == None:
        response_body = {"message": "This record does not exist in our database. Please try again."}
        return make_response(response_body, 404)
    
    if request.method == 'PATCH':
        data = request.get_json()
        for attr in data:
            setattr(message, attr, data[attr])

        db.session.add(message)
        db.session.commit()

        mess_dict = message.to_dict()

        return make_response(jsonify(mess_dict), 200)

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        response_body = {
                "delete_successful": True,
                "message": "Review deleted."
            }

        response = make_response(
            jsonify(response_body),
            200
        )
        return response

if __name__ == '__main__':
    app.run(port=5555)
