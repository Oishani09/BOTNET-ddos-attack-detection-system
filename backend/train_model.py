# Separate script to train and save the model (train_model.py)

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Load the dataset
dataset = pd.read_csv('./D2.csv')  # Adjust path as necessary
X = dataset.drop(columns=['target'])  # Replace 'target' with your actual target column
y = dataset['target']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save the trained model to a file
joblib.dump(model, './randomModel.pkl')
