#!/usr/bin/env python3

import os
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.getenv("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code Challenge</h1>'

@app.route('/heroes')
def get_heroes():
    heroes = [
        {"id": hero.id, "name": hero.name, "super_name": hero.super_name}
        for hero in Hero.query.all()
    ]
    return make_response(jsonify(heroes), 200)

@app.route('/heroes/<int:id>')
def get_hero_by_id(id):
    hero = Hero.query.filter_by(id=id).first()
    if hero:
        return make_response(hero.to_dict(), 200)
    return make_response({"error": "Hero not found"}, 404)

@app.route('/powers')
def get_powers():
    powers = [
        {"id": power.id, "name": power.name, "description": power.description}
        for power in Power.query.all()
    ]
    return make_response(jsonify(powers), 200)

@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def handle_power_by_id(id):
    power = Power.query.filter_by(id=id).first()
    if not power:
        return make_response({"error": "Power not found"}, 404)

    if request.method == 'GET':
        return make_response(power.to_dict(), 200)

    if request.method == 'PATCH':
        data = request.json
        description = data.get('description', '')
        if len(description) < 20:
            return make_response({"errors": ["validation errors"]}, 400)

        for key, value in data.items():
            setattr(power, key, value)

        db.session.commit()
        return make_response(power.to_dict(), 200)

@app.route('/hero_powers', methods=['GET', 'POST'])
def handle_hero_powers():
    if request.method == 'GET':
        hero_powers = [hp.to_dict() for hp in HeroPower.query.all()]
        return make_response(jsonify(hero_powers), 200)

    if request.method == 'POST':
        data = request.json
        strength = data.get('strength')
        if strength not in ['Strong', 'Weak', 'Average']:
            return make_response({"errors": ["validation errors"]}, 400)

        new_hero_power = HeroPower(
            strength=strength,
            power_id=data.get('power_id'),
            hero_id=data.get('hero_id')
        )
        db.session.add(new_hero_power)
        db.session.commit()
        return make_response(new_hero_power.to_dict(), 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
