import pandas as pd
import random
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

input_path = os.path.join(current_dir, 'data_processed', 'merged_processed_dataset.csv')
df = pd.read_csv(input_path)

balanced = 30000

# Function to balance the dataset
def balance_dataset(df, target_count):
    balanced_df = pd.DataFrame(columns=df.columns)
    for emotion in df['Emotion'].unique():
        emotion_subset = df[df['Emotion'] == emotion]
        current_count = len(emotion_subset)

        if current_count > target_count:
            chunk_size = current_count // 10 
            sampled_indices = []
            for i in range(10):
                chunk = emotion_subset.iloc[i * chunk_size: (i + 1) * chunk_size]
                sampled_chunk = chunk.sample(
                    target_count // 10, random_state=42)
                sampled_indices.extend(sampled_chunk.index)
            sampled_subset = emotion_subset.loc[sampled_indices]
        else:
            additional_count = target_count - current_count
            duplicates_needed = []
            while len(duplicates_needed) < additional_count:
                remaining_rows = target_count - \
                    len(duplicates_needed) - current_count
                sampled_rows = random.choices(
                    emotion_subset.index,
                    k=min(remaining_rows, len(emotion_subset.index))
                )
                duplicates_needed += [
                    row for row in sampled_rows if duplicates_needed.count(row) < 3]
            sampled_subset = pd.concat(
                [emotion_subset, emotion_subset.loc[duplicates_needed]], ignore_index=True)

        balanced_df = pd.concat(
            [balanced_df, sampled_subset], ignore_index=True)

    return balanced_df

balanced_df = balance_dataset(df, balanced)

output_path= os.path.join(current_dir, 'data_processed', 'test_dataset.csv')
balanced_df.to_csv(output_path, index=False)

print(f"Balanced dataset saved to: {output_path}")
