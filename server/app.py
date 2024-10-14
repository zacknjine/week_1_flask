from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class HeroResource(Resource):
    def get(self, hero_id):
        hero = Hero.query.get_or_404(hero_id)
        return hero.to_dict()

    def put(self, hero_id):
        hero = Hero.query.get_or_404(hero_id)
        data = request.json
        hero.name = data.get('name', hero.name)
        hero.super_name = data.get('super_name', hero.super_name)
        db.session.commit()
        
        return make_response(hero.to_dict(), 200)

    def delete(self, hero_id):
        hero = Hero.query.get_or_404(hero_id)
        db.session.delete(hero)
        db.session.commit()
        return make_response({'message': 'Hero deleted'}, 204)

class HeroListResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        return [hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes]

class PowerResource(Resource):
    def get(self, power_id):
        power = Power.query.get_or_404(power_id)
        return power.to_dict()

    def put(self, power_id):
        power = Power.query.get_or_404(power_id)
        data = request.json
        power.name = data.get('name', power.name)
        power.description = data.get('description', power.description)
        db.session.commit()
        
        return make_response(power.to_dict(), 200)

    def delete(self, power_id):
        power = Power.query.get_or_404(power_id)
        db.session.delete(power)
        db.session.commit()
        return make_response({'message': 'Power deleted'}, 204)

class PowerListResource(Resource):
    def get(self):
        powers = Power.query.all()
        return [power.to_dict() for power in powers]

class HeroPowerResource(Resource):
    def post(self):
        data = request.json
        if 'strength' not in data or 'hero_id' not in data or 'power_id' not in data:
            return make_response({'error': 'Missing required fields'}, 400)

        new_hero_power = HeroPower(
            strength=data['strength'], 
            hero_id=data['hero_id'], 
            power_id=data['power_id']
        )
        db.session.add(new_hero_power)
        db.session.commit()
        return make_response(new_hero_power.to_dict(), 201)

    def delete(self, hero_power_id):
        hero_power = HeroPower.query.get_or_404(hero_power_id)
        db.session.delete(hero_power)
        db.session.commit()
        return make_response({'message': 'HeroPower deleted'}, 204)

api.add_resource(HeroListResource, '/heroes')
api.add_resource(HeroResource, '/heroes/<int:hero_id>')
api.add_resource(PowerListResource, '/powers')
api.add_resource(PowerResource, '/powers/<int:power_id>')
api.add_resource(HeroPowerResource, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555)
