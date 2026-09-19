from xgboost import XGBClassifier
from inference.inference_functions import gather_match_features

xg_model = XGBClassifier() 
xg_model.load_model("models/xgboost_worldcup_model.json")

features = gather_match_features("FR", "EN", "2026-07-18", "FIFA World Cup", "United States")
prediction = xg_model.predict(features) 

class_names = {
    0: "away_win",
    1: "draw",
    2: "home_win"
}

prediction_label = class_names[prediction[0]] 

print("prediction:", prediction)
print("prediction[0]:", prediction[0])
print("lookup:", class_names[prediction[0]])
print("prediction_label:", prediction_label)


