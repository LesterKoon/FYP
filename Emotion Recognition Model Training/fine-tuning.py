import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import numpy as np
import evaluate
import torch
import glob
import os

# Load datasets
current_dir = os.path.dirname(os.path.abspath(__file__))
train_df = pd.read_csv(os.path.join(current_dir, 'data', 'train_dataset.csv'))
val_df = pd.read_csv(os.path.join(current_dir, 'data', 'val_dataset.csv'))

# Convert to HuggingFace datasets
train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)

# Load tokenizer
model_name = "j-hartmann/emotion-english-distilroberta-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Define tokenization function
def tokenize_function(examples):
    texts = examples['text']
    if isinstance(texts, str):
        texts = [texts]

    texts = [str(t) if t is not None else "" for t in texts]

    return tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors=None
    )

# Tokenize datasets
print("Tokenizing datasets...")
tokenized_train = train_dataset.map(
    tokenize_function,
    batched=True,
    batch_size=1000,
    remove_columns=train_dataset.column_names,
    desc="Tokenizing train dataset"
)

tokenized_val = val_dataset.map(
    tokenize_function,
    batched=True,
    batch_size=1000,
    remove_columns=val_dataset.column_names,
    desc="Tokenizing validation dataset"
)

# Add back the labels
tokenized_train = tokenized_train.add_column("labels", train_dataset["label"])
tokenized_val = tokenized_val.add_column("labels", val_dataset["label"])

# Set format for PyTorch
tokenized_train.set_format("torch")
tokenized_val.set_format("torch")

# Load model with ignore_mismatched_sizes=True
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=8,
    ignore_mismatched_sizes=True
)

# Define metrics
accuracy_metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return accuracy_metric.compute(predictions=predictions, references=labels)


# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="steps",
    save_strategy="steps",
    save_steps=200, 
    learning_rate=3e-5,
    num_train_epochs=3,
    per_device_train_batch_size=64,
    per_device_eval_batch_size=64,
    logging_dir="./logs",
    logging_steps=200,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy"
)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# Train model
print("Training the model...")
trainer.train()


# Save model
model.save_pretrained("./fine_tuned_emotion_model")
tokenizer.save_pretrained("./fine_tuned_emotion_model")
print("Fine-tuned model saved to ./fine_tuned_emotion_model")

# Test the model
emotion_mapping = {
    0: "Happy", 1: "Excited", 2: "Energetic", 3: "Fear",
    4: "Sad", 5: "Depressed", 6: "Calm", 7: "Angry"
}

test_text = "I'm feeling very happy today!"
inputs = tokenizer(test_text, return_tensors="pt",
                   truncation=True, padding=True)
outputs = model(**inputs)
predicted_class = torch.argmax(outputs.logits).item()
predicted_emotion = emotion_mapping[predicted_class]
print(f"Test prediction - Text: '{test_text}' -> Emotion: {predicted_emotion}")
