from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder,OneHotEncoder, StandardScaler
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from sklearn.ensemble import RandomForestClassifier

app = FastAPI()

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
    )  
                
# loading Encoders & Model
with open(r"C:\Users\RPC\Desktop\jupyter files\machine learning & data science projects-github\Car_Price_Predition_Project\label_encoders.pkl", "rb") as f:
    label_encoders = pickle.load(f)

with open(r"C:\Users\RPC\Desktop\jupyter files\machine learning & data science projects-github\Car_Price_Predition_Project\One_Hot_Encoder.pkl", "rb") as f:
    One_Hot_Encoder = pickle.load(f)

with open (r"C:\Users\RPC\Desktop\jupyter files\machine learning & data science projects-github\Car_Price_Predition_Project\scaler.pkl", "rb") as file : 
    scaler = pickle.load(file)

with open(r"C:\Users\RPC\Desktop\jupyter files\machine learning & data science projects-github\Car_Price_Predition_Project\RandomForestRegressor_model.pkl","rb") as file2 : 
     RandomForestRegressor_model = pickle.load(file2)

class CarInput(BaseModel):
    Levy:int
    Manufacturer:str
    Model:str
    Prod_year:int
    Category: str
    Leather_interior: str
    Fuel_type: str 
    Engine_volume: float 
    Mileage: int
    Cylinders: float 
    Gear_box_type: str
    Drive_wheels: str 
    Wheel: str 
    Color: str
    Airbags: int

@app.post("/predict/")
def predict(car_data:CarInput):
    
    try :

        df = pd.DataFrame([car_data.dict()])
        # Feature Extraction
        df["Age_of_Car"] = datetime.now().year - df["Prod_year"]

        # Label Encoder
        label_encoder_columns = ["Manufacturer", "Model", "Category","Fuel_type", "Color","Leather_interior","Wheel"]
        for col in label_encoder_columns:
            if col in label_encoders:  
                label = label_encoders[col]
            
                unseen_values = set(df[col]) - set(label.classes_)
                if unseen_values:
                    label.classes_ = np.append(label.classes_, list(unseen_values))  

                df[col] = label.transform(df[col])
            else:
                print(f"Warning: No encoder found for column {col}")
        
        # One Hot Encoder
        one_hot_columns = ["Gear_box_type","Drive_wheels"]
        ohe_encoded_data = One_Hot_Encoder.transform(df[one_hot_columns])
        ohe_encoded_data_df = pd.DataFrame(ohe_encoded_data, columns=One_Hot_Encoder.get_feature_names_out(one_hot_columns), index=df.index)
        df2 = pd.concat([df, ohe_encoded_data_df], axis=1)
        df2.drop(columns=one_hot_columns, inplace=True)

        order_in_fit = ['Levy', 'Prod_year', 'Engine_volume', 'Mileage', 'Cylinders', 'Airbags',
                        'Age_of_Car', 'Manufacturer', 'Model', 'Category', 'Fuel_type', 'Color',
                        'Leather_interior', 'Wheel', 'Gear_box_type_Automatic',
                        'Gear_box_type_Manual', 'Gear_box_type_Tiptronic',
                        'Gear_box_type_Variator', 'Drive_wheels_4x4', 'Drive_wheels_Front',
                        'Drive_wheels_Rear']

        df2 = df2[order_in_fit]

        # Feature Scaling
        Scaling_feature = ["Levy", "Engine_volume", "Mileage", "Age_of_Car"]
        df2[Scaling_feature] = scaler.transform(df2[Scaling_feature])

        # Prediction
        prediction =  RandomForestRegressor_model.predict(df2)
        return {"Prediction":float(prediction[0])}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

