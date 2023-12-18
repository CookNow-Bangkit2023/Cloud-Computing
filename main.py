import json
from flask import Flask, jsonify, request
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, and_
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

with open("clean_recipes.json") as f:
    recipes = json.load(f)

@app.route('/', methods=['GET'])
def test():
    return 'Put URL'

@app.route('/api/rating', methods = ['POST'])
def post_rating():
    try:
        session = Session()
        data = request.get_json()
        existing_rating = session.query(UserRecipeRating).filter(
            and_(
                UserRecipeRating.user_id == data['user_id'],
                UserRecipeRating.recipe_id == data['recipe_id']
            )
        ).first()
        if existing_rating:
            existing_rating.rating = data['rating']
        else :
            new_rating = UserRecipeRating(
                user_id=data['user_id'],
                recipe_id=data['recipe_id'],
                date=datetime.now(),
                rating=data['rating']
            )
            session.add(new_rating)
        session.commit()
        session.close()
        return jsonify({'message': 'Rating added/updated successfully'}), 201
    except Exception as e:
        print("Error:", e)
        return {'error': f'Failed to fetch data from the databases. Error details: {str(e)}'}, 500

@app.route("/api/recipes", methods=["GET"])
def get_recipes():
    try:
        session = Session()
        results = session.query(Recipe.id, Recipe.name).order_by(func.rand()).limit(10).all()
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

@app.route("/api/recipe/rating/<int:recipe_id>", methods=["GET"])
def get_recipe_with_ratings(recipe_id):
    try:
        session = Session()
        result = session.execute(select(UserRecipeRating.rating).where(UserRecipeRating.recipe_id == recipe_id))
        ratings = [row[0] for row in result]
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