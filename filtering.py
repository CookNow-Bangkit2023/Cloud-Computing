import tensorflow as tf
import numpy as np

def filter_recipe(user_input, recipes):
    matched_recipes = []

    for row in recipes:
        label, ingre = row.values()
        if all(i in user_input for i in ingre):
            matched_recipes.append(label)

    return matched_recipes

def predict(user_input, recipes):
    user_input = user_input
    reccomendation = filter_recipe(user_input, recipes)

    if reccomendation:
        return reccomendation[0:10]
    else:
        return ["error"]

def get_rating(user_id, recipes_id):
    interpreter = tf.lite.Interpreter(model_path="converted_model.tflite")
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]["index"], np.array([user_id]))
    interpreter.set_tensor(input_details[1]["index"], np.array([recipes_id]))

    interpreter.invoke()

    rating = interpreter.get_tensor(output_details[0]['index'])

    return rating

def ranking(user_id, recipes_id):
    result = []

    for id in recipes_id:
        rating = get_rating(user_id, id)
        result.append([id, float(rating)])

    return sorted(result, key=lambda x :x[1], reverse=True)