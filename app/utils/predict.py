import joblib
import numpy as np

child_model = joblib.load("app/model/model.pkl")
adult_model = joblib.load("app/model/adult_model.pkl")

def predict_autism(data, age):

    input_data = np.array(data).reshape(1, -1)

    if age < 18:
        prediction = child_model.predict(input_data)
    else:
        prediction = adult_model.predict(input_data)

    return int(prediction[0])