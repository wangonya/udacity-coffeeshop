import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
import sqlite3
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
# db_drop_and_create_all()


# ROUTES

@app.route('/drinks')
def get_all_drinks():
    try:
        drinks = Drink.query.all()
        drinks = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except:
        abort(422)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        drinks = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except:
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks():
    try:
        data = request.get_json()['title'] and request.get_json()['recipe']
        if not data:
            abort(400)
    except (TypeError, KeyError):
        abort(400)

    # drink title must be unique
    if Drink.query.filter_by(title=request.get_json()['title']).first():
        abort(409)

    try:
        Drink(
            title=request.get_json()['title'],
            recipe=json.dumps(request.get_json()['recipe'])
        ).insert()
        drink = Drink.query.filter_by(title=request.get_json()['title']).first()
        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 201
    except:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(drink_id):
    try:
        data = request.get_json()['title'] or request.get_json()['recipe']
        if not data:
            abort(400)
    except (TypeError, KeyError):
        abort(400)

    drink = Drink.query.filter_by(id=drink_id).first()
    if not drink:
        abort(404)

    try:
        if request.get_json()['title']:
            drink.title = request.get_json()['title']
        if request.get_json()['recipe']:
            drink.recipe = json.dumps(request.get_json()['recipe'])
        drink.update()
        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(drink_id):
    drink = Drink.query.filter_by(id=drink_id).first()
    if not drink:
        abort(404)

    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200
    except Exception:
        abort(422)


# Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404


@app.errorhandler(409)
def duplicate(error):
    return jsonify({
        "success": False,
        "error": 409,
        "message": "duplicate"
    }), 409


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
