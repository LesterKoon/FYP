import pandas as pd
import matplotlib.pyplot as plt
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

def list_emotions_and_counts(file_path):
    df = pd.read_csv(file_path)

    emotion_counts = df['Emotion'].value_counts()

    print("Emotion Counts:")
    for emotion, count in emotion_counts.items():
        print(f"{emotion}: {count}")

    return emotion_counts

input_path = os.path.join(current_dir, 'data_processed', 'final_dataset.csv')

emotion_counts = list_emotions_and_counts(input_path)

plt.figure(figsize=(10, 6))
emotion_counts.plot(kind='bar', edgecolor='black')
plt.title("Distribution of Emotions in Dataset", fontsize=16)
plt.xlabel("Emotions", fontsize=14)
plt.ylabel("Counts", fontsize=14)
plt.xticks(rotation=45, fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout() 
plt.show()
