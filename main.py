import json
from flask import Flask, jsonify, request
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import select, func
from model import Recipe, UserRecipeRating
from filtering import predict as predictable
from filtering import ranking as ranked
import os
from datetime import datetime

app = Flask(__name__)

engine_str = (
    "mysql+pymysql://{user}:{password}@{server}/{database}".format(
        user="root",
        password="qwerty12345",
        server="34.101.54.86",
        database="capstone",
    )
)

engine = sa.create_engine(engine_str)
Session = sessionmaker(bind=engine)

try:
    with engine.connect() as connection:
        print("Connection successful")

    with Session() as session:
        print("Session created successfully")
except Exception as e:
    print("Error:", e)
    print("Connection failed")

with open("clean_recipes.json") as f:
    recipes = json.load(f)

@app.route('/', methods=['GET'])
def test():
    return 'Put URL'
#rating


@app.route('/api/rating/<int:recipe_id>', methods=['GET'])
def get_rating(recipe_id):
    try:
        session = Session()
        result = session.execute(select(UserRecipeRating.rating).where(UserRecipeRating.recipe_id == recipe_id))
        ratings = [row[0] for row in result]
        average_rating = round(sum(ratings) / len(ratings), 2) if ratings and len(ratings) > 0 else None
        session.close()
        return jsonify({
            'average_rating': average_rating
        })
    except Exception as e:
        print("Error:", e)
        return {'error': f'Failed to fetch data from the databases. Error details: {str(e)}'}, 500

@app.route('/api/rating', methods = ['POST'])
def post_rating():
    try:
        session = Session()
        data = request.get_json()
        new_rating = UserRecipeRating(
            user_id=data['user_id'],
            recipe_id=data['recipe_id'],
            date=datetime.now(),
            rating=data['rating']
        )
        session.add(new_rating)
        session.commit()
        session.close()
        return jsonify({'message': 'Rating added successfully'}), 201
    except Exception as e:
        print("Error:", e)
        return {'error': f'Failed to fetch data from the databases. Error details: {str(e)}'}, 500


@app.route('/api/rating', methods=['PUT'])
def put_rating():
    try:
        session = Session()
        data = request.get_json()
        print("Received data:", data)
        existing_rating = session.query(UserRecipeRating).filter_by(
            user_id=data['user_id'],
            recipe_id=data['recipe_id'],
        ).first()
        print("Existing rating:", existing_rating)
        if existing_rating:
            existing_rating.rating = data['rating']
            session.commit()
            session.close()
            return jsonify({'message': 'Rating updated successfully'}), 200
        else:
            session.close()
            return jsonify({'error': 'Rating not found'}), 404
    except Exception as e:
        print("Error:", e)
        return {'error': f'Failed to fetch data from the databases. Error details: {str(e)}'}, 500

@app.route('/api/rating', methods = ['DELETE'])
def delete_rating():
    try:
        session = Session()
        data = request.get_json()
        rating_to_delete = session.query(UserRecipeRating).filter_by(
            user_id=data['user_id'],
            recipe_id=data['recipe_id']
        ).first()
        if rating_to_delete:
            session.delete(rating_to_delete)
            session.commit()
            session.close()
            return jsonify({'message': 'Rating deleted successfully'}), 200
        else:
            session.close()
            return jsonify({'error': 'Rating not found'}), 404
    except Exception as e:
        print("Error:", e)
        return {'error': f'Failed to fetch data from the databases. Error details: {str(e)}'}, 500




@app.route("/api/recipes", methods=["GET"])
def get_recipes_v1():
    try:
        session = Session()
        results = session.query(Recipe.id, Recipe.name).order_by(func.rand()).limit(10).all()
        session.close()
        recipes_list = [{'id': result.id, 'name': result.name} for result in results]
        return jsonify(recipes_list)
    except Exception as e:
        print("Error:", e)
        return {'error': f'Failed to fetch data from the databases. Error details: {str(e)}'}, 500

@app.route("/api/v2/recipes/<int:many>", methods=["GET"])
def get_recipes_v2(many):
    try:
        session = Session()
        results = session.query(Recipe.id, Recipe.name).order_by(func.rand()).limit(many).all()
        session.close()
        recipes_list = [{'id': result.id, 'name': result.name} for result in results]
        return jsonify(recipes_list)
    except Exception as e:
        print("Error:", e)
        return {'error': f'Failed to fetch data from the databases. Error details: {str(e)}'}, 500

@app.route("/api/predict", methods=["POST"])
def get_predict():
    try:
        data = request.get_json()
        filtered = predictable(list(data["ingres"]), recipes)
        prediction = ranked(data["user_id"], filtered)
        
        extracted_values = [int(item[0]) for item in prediction]
        results_from_database = search_database_by_ids(extracted_values)
        return results_from_database
    except Exception as e:
        print("Unexpected error:", e)
        return {'error': f'Failed to fetch data from the databases. Error details: {str(e)}'}, 500
def search_database_by_ids(ids):
    try:
        session = Session()
        results = session.query(Recipe).filter(Recipe.id.in_(ids)).limit(10).all()
        session.close()
        recipes_list = [
            {
                'id': result.id,
                'name': result.name,
            }
            for result in results
        ]
        return jsonify(recipes_list)
    except Exception as e:
        print("Unexpected error:", e)
        return {'error': f'Failed to fetch data from the databases. Error details: {str(e)}'}, 500
    
@app.route("/api/v2/predict/<int:many>", methods=["POST"])
def get_predict_v2(many):
    try:
        data = request.get_json()
        filtered = predictable(list(data["ingres"]), recipes)
        prediction = ranked(data["user_id"], filtered)
        
        extracted_values = [int(item[0]) for item in prediction]
        results_from_database = search_database_by_ids_v2(extracted_values, many)
        return results_from_database
    except Exception as e:
        print("Unexpected error:", e)
        return {'error': f'Failed to fetch data from the databases. Error details: {str(e)}'}, 500
def search_database_by_ids_v2(ids, many):
    try:
        session = Session()
        results = session.query(Recipe).filter(Recipe.id.in_(ids)).limit(many).all()
        session.close()
        recipes_list = [
            {
                'id': result.id,
                'name': result.name,
            }
            for result in results
        ]
        return jsonify(recipes_list)
    except Exception as e:
        print("Unexpected error:", e)
        return {'error': f'Failed to fetch data from the databases. Error details: {str(e)}'}, 500

@app.route("/api/recipe/rating/<int:recipe_id>", methods=["GET"])
def get_recipe_with_ratings(recipe_id):
    try:
        session = Session()
        results_rating = session.execute(select(UserRecipeRating).where(UserRecipeRating.recipe_id == recipe_id))
        ratings = [dict(row) for row in results_rating]
        average_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
        results_recipe = (session.query(Recipe)
            .filter(Recipe.id == recipe_id)
            .first()
        )
        session.close()
        recipe_data = {
            'id': results_recipe.id,
            'name': results_recipe.name,
            'steps': results_recipe.steps,
            'ingredients': results_recipe.ingredients,
            'n_steps' : results_recipe.n_steps,
            'n_ingridients' : results_recipe.n_ingredients,
            'minutes' : results_recipe.minutes
        }
        return jsonify({
            'result_recipe': recipe_data,
            'average_rating': average_rating
        })
    except Exception as e:
        print("Error:", e)
        return {'error': f'Failed to fetch data from the databases. Error details: {str(e)}'}, 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
