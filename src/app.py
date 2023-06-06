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
from models import db, User, Planet, People, Favorite, FavoritePeople
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
people=[]

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



from flask import request, jsonify
#Endpoint para Hacer Post en People
@app.route('/people', methods=['POST'])
def add_person():
    data = request.get_json()
    new_person = People(name=data['name'])
    db.session.add(new_person)
    db.session.commit()

  
    return jsonify({
        'id': new_person.id,
        'name': new_person.name
       
    }), 201


#Endpoint para hacer el GET de Todos los people
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    result = []
    for person in people:
        result.append({
            'id': person.id,
            'name': person.name
        })
    return jsonify(result)


#Endpoint para hacer el Get de un people en especifico pasando como parametro el id
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({'error': 'Person not found'}), 404
    return jsonify({
        'id': person.id,
        'name': person.name
        # Agrega más atributos según tus necesidades
    })


#Endpoint para hacer Post en planetas
@app.route('/planets', methods=['POST'])
def add_planet():
    data = request.get_json()
    new_planet = Planet(name=data['name'])
    db.session.add(new_planet)
    db.session.commit()

  
    return jsonify({
        'id': new_planet.id,
        'name': new_planet.name
       
    }), 201


#Endpoint para hacer Get de todos los planetas
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    result = []
    for planet in planets:
        result.append({
            'id': planet.id,
            'name': planet.name
            # Agrega más atributos según tus necesidades
        })
    return jsonify(result)


#Endpoint para hacer el get de un planeta en especifico pasando el id como parametro
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({'error': 'Planet not found'}), 404
    return jsonify({
        'id': planet.id,
        'name': planet.name
        # Agrega más atributos según tus necesidades
    })

  
#Endpoint para hacer el Get de todos los  User
@app.route('/user', methods=['GET'])
def handle_hello():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'email': user.email
        })
    return jsonify(result)


#Endpoint para  ver los planetas y people favoritos de un usuario en especifico donde pasamos el usuario a traves del id.
@app.route('/user/favorites/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    favorite_planets = Favorite.query.filter_by(user_id=user.id).all()
    favorite_people = FavoritePeople.query.filter_by(user_id=user.id).all()

    result = {
        'user_id': user.id,
        'favorite_planets': [],
        'favorite_people': []
    }

    for fp in favorite_planets:
        result['favorite_planets'].append({
            'favorite_id': fp.id,
            'planet_id': fp.planet.id,
            'planet_name': fp.planet.name
        })

    for fp in favorite_people:
        result['favorite_people'].append({
            'favorite_id': fp.id,
            'people_id': fp.people.id,
            'people_name': fp.people.name
        })

    return jsonify(result)


        
#En este endpoint hacemos Post en la tabla favoritos de un planeta a un usuario que pasamos por el id. 
@app.route('/user/favorites/<int:user_id>', methods=['POST'])
def add_favorite_planet(user_id):
    # Obtener el usuario actual (puedes adaptar esta lógica según tu implementación)
    user = User.query.get(user_id)  # Función para obtener el usuario actual

    # Verificar si el usuario existe
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    planet_id = request.get_json()["planet_id"]
    # Verificar si el planeta existe
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({'error': 'Planet not found'}), 404

    # Agregar el planeta favorito al usuario
    favorite = Favorite(user=user, planet=planet)
    db.session.add(favorite)
    db.session.commit()

    # Devolver la respuesta con los datos del planeta agregado al usuario
    return jsonify({
        'user_id': user.id,
        'planet_id': planet.id
        # Agrega más atributos según tus necesidades
    }), 201


#Aca agrego a la tabla favorite-people un  people a un usuario en especifico.
@app.route('/user/favorite-people/<int:user_id>', methods=['POST'])
def add_favorite_people(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    people_id = data.get('people_id')
    if people_id is None:
        return jsonify({'error': 'Invalid request'}), 400

    people = People.query.get(people_id)
    if people is None:
        return jsonify({'error': 'People not found'}), 404

    favorite_people = FavoritePeople(user=user, people=people)
    db.session.add(favorite_people)
    db.session.commit()

    return jsonify({
        'user_id': user.id,
        'people_id': people.id
    }), 201


#aqui elimino un planeta de la lista favoritos de un usuario donde paso como parametro el id del planeta y del usuario en la ruta

@app.route('/user/favorites/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        return jsonify({'error': 'Favorite planet not found for the user'}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'message': 'Favorite planet deleted successfully'})


#En este ultimo endpoint eliminammos un people de la tabla favoritos de un usuario en especifico

@app.route('/user/favorites/<int:user_id>/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(user_id, people_id):
    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite is None:
        return jsonify({'error': 'Favorite person not found for the user'}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'message': 'Favorite person deleted successfully'})




# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
