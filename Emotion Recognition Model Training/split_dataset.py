import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(current_dir, 'data', 'balanced_dataset.csv')
df = pd.read_csv(file_path)

df = df.rename(columns={"Text": "text"})
df = df.rename(columns={"Emotion": "label"})  # Replace with your dataset file

# Map emotion labels to integers for stratification
emotion_mapping = {
    "Happy": 0,
    "Excited": 1,
    "Energetic": 2,
    "Fear": 3,
    "Sad": 4,
    "Depressed": 5,
    "Calm": 6,
    "Angry": 7
}
df["label"] = df["label"].map(emotion_mapping)

# Perform a stratified split
train_df, val_df = train_test_split(
    df,
    test_size=0.2,  # 80% train, 20% validation
    stratify=df["label"],  # Ensure stratified split
    random_state=42  # Seed for reproducibility
)

train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)

train_file = os.path.join(current_dir, 'data', 'train_dataset.csv')
val_file = os.path.join(current_dir, 'data', 'validation_dataset.csv')
train_df.to_csv(train_file, index=False)
val_df.to_csv(val_file, index=False)

print("Datasets saved as train_dataset.csv and validation_dataset.csv")
