from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
        }
    
class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    terrain = db.Column(db.String(150), nullable=False)
    climate = db.Column(db.Enum('arid', 'temperate', 'tropical', 'frozen', 'murky', name='climate_types'), nullable=False)
    population = db.Column(db.String(100), nullable=False)
    orbital_period = db.Column(db.Integer, nullable=False)
    rotation_period = db.Column(db.Integer, nullable=False)
    diameter = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    image_url = db.Column(db.String(500))

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "terrain": self.terrain,
            "climate": self.climate,
            "population": self.population,
            "orbital_period": self.orbital_period,
            "rotation_period": self.rotation_period,
            "diameter": self.diameter,
            "description": self.description,
            "image_url": self.image_url
        }

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    gender = db.Column(db.Enum('female', 'male', 'other', 'n/a', name="gender_types"), nullable=False)
    birth_year = db.Column(db.String(50), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    hair_color = db.Column(db.String(50), nullable=False)
    eye_color = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    image_url = db.Column(db.String(500))
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    planet = db.relationship(Planet)

    def __repr__(self):
        return '<Character %r>' % self.name

    def serialize(self):
        planet_name = self.planet.name if self.planet else None
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "birth_year": self.birth_year,
            "height": self.height,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "homeworld": planet_name,
            "description": self.description,
            "image_url": self.image_url
        }

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    vehicle_class = db.Column(db.String(150), nullable=False)
    manufacturer = db.Column(db.String(200), nullable=False)
    length = db.Column(db.String(10), nullable=False)
    passengers = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    image_url = db.Column(db.String(500))
    pilot_id = db.Column(db.Integer, db.ForeignKey('character.id'))
    character = db.relationship(Character)

    def __repr__(self):
        return '<Vehicle %r>' % self.name

    def serialize(self):
        pilot_name = self.character.name if self.character else None
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "vehicle_class": self.vehicle_class,
            "manufacturer": self.manufacturer,
            "length": self.length,
            "passengers": self.passengers,
            "pilot_id": pilot_name,
            "description": self.description,
            "image_url": self.image_url
        }
    
class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    user = db.relationship(User)
    character = db.relationship(Character)
    planet = db.relationship(Planet)
    vehicle = db.relationship(Vehicle)

    def __repr__(self):
        return '<Favorites %r>' % self.user_id

    def serialize(self):
        characters = [favorite.character.name for favorite in Favorites.query.filter(Favorites.character_id.isnot(None)).all()]
        planets = [favorite.planet.name for favorite in Favorites.query.filter(Favorites.planet_id.isnot(None)).all()]
        vehicles = [favorite.vehicle.name for favorite in Favorites.query.filter(Favorites.vehicle_id.isnot(None)).all()]
        return {
            "character_id": characters,
            "planets": planets,
            "vehicle_id": vehicles
        }