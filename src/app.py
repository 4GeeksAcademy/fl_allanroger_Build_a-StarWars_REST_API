"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Vehicle, Favorites


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# USERS ENDPOINTS
# -----------------------------------Get All Users--------------------------------
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    serialized_users = [user.serialize() for user in users]

    if users is None:
        return jsonify({'error':'No users found'}), 404
    else:
        return jsonify(serialized_users), 200


# FAVORITES ENDPOINTS
# -----------------------------------Get All Favorites of a User--------------------------------
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error':'User not found'}), 404
    
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    
    if favorites is None:
        return jsonify({'error':'Favorites not found for this user'}), 404
    else:
        combined_favorites = {
        "favorite_characters": [],
        "favorite_planets": [],
        "favorite_vehicles": []
    }
        for favorite in favorites:
            if favorite.character:
                combined_favorites["favorite_characters"].append(favorite.character.name)
            if favorite.planet:
                combined_favorites["favorite_planets"].append(favorite.planet.name)
            if favorite.vehicle:
                combined_favorites["favorite_vehicles"].append(favorite.vehicle.name)
        return jsonify(combined_favorites), 200

# ---------------------Add Favorite Planet/Character/Vehicle to a User-------------------------
@app.route('/favorites/user/<int:user_id>', methods=['POST'])
def add_favorite(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error':'User not found'}), 404
    
    body = request.get_json()
    favorites = Favorites()
    favorites.user_id = user_id
    favorites.character_id = body.get('character_id')
    favorites.planet_id = body.get('planet_id')
    favorites.vehicle_id = body.get('vehicle_id')

    db.session.add(favorites)
    db.session.commit()

    return jsonify({'msg':'Favorites have been updated successfully'}), 200

# ---------------------Delete Favorite Planet/Character/Vehicle of a User-------------------------
@app.route('/favorites/users/<int:user_id>/<string:type>/<int:id>', methods=['DELETE'])
def delete_favorite(user_id, id, type):
    user = User.query.get(user_id)
    favorite_entry = ''
    if user is None:
        return jsonify({'error':'User not found'}), 404
    
    if type == 'planet':
        favorite_entry = Favorites.query.filter_by(user_id=user_id, planet_id=id).first()
    elif type == 'character':
        favorite_entry = Favorites.query.filter_by(user_id=user_id, character_id=id).first()
    elif type == 'vehicle':
        favorite_entry = Favorites.query.filter_by(user_id=user_id, vehicle_id=id).first()

    if favorite_entry:
        db.session.delete(favorite_entry)
        db.session.commit()
        return jsonify({'msg':f'Favorite {type} deleted successfully'}), 200
    else:
        return jsonify({'error':f'Favorite {type} not found'}), 404


# CHARACTERS ENDPOINTS
# -----------------------------------Get All Characters--------------------------------
@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    serialized_characters = [character.serialize() for character in characters]

    if characters is None:
        return jsonify({'error':'No characters found'}), 404
    else:
        return jsonify(serialized_characters), 200

# -----------------------------------Get a Character--------------------------------
@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.get(character_id)

    if character is None:
        return jsonify({'error': 'Character not found'}), 404
    else:
        return jsonify(character.serialize()), 200

# -----------------------------------Add a Character--------------------------------
@app.route('/characters', methods=['POST'])
def add_character():
    body = request.get_json()
    character = Character()
    character.name = body.get('name')
    character.gender = body.get('gender')
    character.birth_year = body.get('birth_year')
    character.height = body.get('height')
    character.hair_color = body.get('hair_color')
    character.eye_color = body.get('eye_color')
    character.description = body.get('description')
    character.image_url = body.get('image_url')
    character.planet_id = body.get('planet_id')

    db.session.add(character)
    db.session.commit()

    return jsonify("Character created successfully", character.serialize()), 200

# -----------------------------------Update a Character--------------------------------
@app.route('/characters/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    body = request.get_json()
    character = Character.query.filter_by(id=character_id).first()

    if character:
        character.name = body.get('name')
        character.gender = body.get('gender')
        character.birth_year = body.get('birth_year')
        character.height = body.get('height')
        character.hair_color = body.get('hair_color')
        character.eye_color = body.get('eye_color')
        character.description = body.get('description')
        character.image_url = body.get('image_url')
        character.planet_id = body.get('planet_id')

    db.session.commit()

    return jsonify("Character has been updated successfully", character.serialize()), 200

# -----------------------------------Delete a Character--------------------------------
@app.route('/characters/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = Character.query.filter_by(id=character_id).first()
    
    if character:
        db.session.delete(character)
        db.session.commit()
        return jsonify("Character deleted successfully"), 200
    else:
        return jsonify("Character not found"), 404


# PLANETS ENDPOINTS
# -----------------------------------Get All Planets--------------------------------
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    serialized_planets = [planet.serialize() for planet in planets]

    if planets is None:
        return jsonify({'error':'No planets found'}), 404
    else:
        return jsonify(serialized_planets), 200

# -----------------------------------Get a Planet--------------------------------
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    
    if planet is None:
        return jsonify({'error':'Planet not found'}), 404
    else:
        return jsonify(planet.serialize()), 200

# -----------------------------------Add a Planet--------------------------------
@app.route('/planets', methods=['POST'])
def add_planet():
    body = request.get_json()
    planet = Planet()
    planet.name = body.get('name')
    planet.terrain = body.get('terrain')
    planet.climate = body.get('climate')
    planet.population = body.get('population')
    planet.orbital_period = body.get('orbital_period')
    planet.rotation_period = body.get('rotation_period')
    planet.diameter = body.get('diameter')
    planet.description = body.get('description')
    planet.image_url = body.get('image_url')

    db.session.add(planet)
    db.session.commit()

    return jsonify("Planet created successfully", planet.serialize()), 200

# -----------------------------------Update a Planet--------------------------------
@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    body = request.get_json()
    planet = Planet.query.filter_by(id=planet_id).first()

    if planet:
        planet.name = body.get('name')
        planet.terrain = body.get('terrain')
        planet.climate = body.get('climate')
        planet.population = body.get('population')
        planet.orbital_period = body.get('orbital_period')
        planet.rotation_period = body.get('rotation_period')
        planet.diameter = body.get('diameter')
        planet.description = body.get('description')
        planet.image_url = body.get('image_url')

    db.session.commit()

    return jsonify("Planet has been updated successfully", planet.serialize()), 200

# -----------------------------------Delete a Planet--------------------------------
@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.filter_by(id=planet_id).first()
    
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify("Planet deleted successfully"), 200
    else:
        return jsonify("Planet not found"), 404


# VEHICLES ENDPOINTS
# -----------------------------------Get All Vehicles--------------------------------
@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = Vehicle.query.all()
    serialized_vehicles = [vehicle.serialize() for vehicle in vehicles]

    if vehicles is None:
        return jsonify({'error':'No vehicles found'}), 404
    else:
        return jsonify(serialized_vehicles), 200

# -----------------------------------Get a Vehicle--------------------------------
@app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    
    if vehicle is None:
        return jsonify({'error':'Vehicle not found'}), 404
    else:
        return jsonify(vehicle.serialize()), 200

# -----------------------------------Add a Vehicle--------------------------------
@app.route('/vehicles', methods=['POST'])
def add_vehicle():
    body = request.get_json()
    vehicle = Vehicle()
    vehicle.name = body.get('name')
    vehicle.model = body.get('model')
    vehicle.model = body.get('model')
    vehicle.vehicle_class = body.get('vehicle_class')
    vehicle.manufacturer = body.get('manufacturer')
    vehicle.length = body.get('length')
    vehicle.passengers = body.get('passengers')
    vehicle.description = body.get('description')
    vehicle.image_url = body.get('image_url')
    vehicle.pilot_id = body.get('pilot_id')

    db.session.add(vehicle)
    db.session.commit()

    return jsonify("Vehicle created successfully", vehicle.serialize()), 200

# -----------------------------------Update a Vehicle--------------------------------
@app.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    body = request.get_json()
    vehicle = Vehicle.query.filter_by(id=vehicle_id).first()

    if vehicle:
        vehicle.name = body.get('name')
        vehicle.model = body.get('model')
        vehicle.model = body.get('model')
        vehicle.vehicle_class = body.get('vehicle_class')
        vehicle.manufacturer = body.get('manufacturer')
        vehicle.length = body.get('length')
        vehicle.passengers = body.get('passengers')
        vehicle.description = body.get('description')
        vehicle.image_url = body.get('image_url')
        vehicle.pilot_id = body.get('pilot_id')

    db.session.commit()

    return jsonify("Vehicle has been updated successfully", vehicle.serialize()), 200

# -----------------------------------Delete a Vehicle--------------------------------
@app.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.filter_by(id=vehicle_id).first()
    
    if vehicle:
        db.session.delete(vehicle)
        db.session.commit()
        return jsonify("Vehicle deleted successfully"), 200
    else:
        return jsonify("Vehicle not found"), 404

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)