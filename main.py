from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    # Serialising the database i.e. convert into a dictionary and then jsonify.
    def row_to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# Returns homepage
@app.route("/")
def home():
    return render_template("index.html")


# Fetches a random café from the database and return the cafe as a JSON
@app.route('/random')
def fetch_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.row_to_dict())


#  Fetches all the cafes in the database and return all the cafes as a JSON.
@app.route('/all')
def get_all():
    all_cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.row_to_dict() for cafe in all_cafes])


# Searches for and return all the cafes at a particular location
@app.route('/search')
def search_by_location():
    area = request.args.get('loc').title()
    cafe_location = Cafe.query.filter_by(location=area).all()
    if len(cafe_location) != 0:
        return jsonify(cafes=[cafe.row_to_dict() for cafe in cafe_location])
    else:
        return jsonify(error={'Not Found': 'Sorry, we don\'t have a cafe at that location.'})


# Adds a new cafe to the database
@app.route('/add', methods=['POST'])
def add_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={'Success': 'Succesfully added the new cafe.'})


# Updates the coffee_price of the cafe and gives the correct feedback if successful or if id in the route doesn't exist
@app.route('/update-price/<int:cafes_id>', methods=['GET', 'PATCH'])
def update_info(cafes_id):
    new_price = request.args.get('new_price')
    cafe_to_update = db.session.query(Cafe).get(cafes_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = f'£{float(new_price)}0'
        db.session.commit()
        return jsonify(response={'Success': 'Succesfully deleted the new cafe.'}), 200
    else:
        return jsonify(error={'Not Found': 'Sorry, a cafe with that id was not found in the database.'}), 404


# Deletes a closed cafe, gives feedback if successful or not
@app.route('/report-closed/<cafe_id>', methods=['GET', 'DELETE'])
def delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    api_key = request.args.get('api-key')
    if api_key == 'Topsecret':
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={'Success': 'Succesfully added the new cafe.'}), 200
        else:
            return jsonify(error={'Not Found': 'Sorry, a cafe with that id was not found in the database.'}), 404
    else:
        return jsonify(error={'Not Found': 'Sorry, that\'s not allowed. Make sure you have the correct api_key'}), 400


if __name__ == '__main__':
    app.run(debug=True)
