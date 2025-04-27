import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

def load_model_and_tokenizer(model_path):
    """Load the fine-tuned model and tokenizer"""
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()  # Set to evaluation mode
    return model, tokenizer


def get_emotion_weights(text, model, tokenizer):
    """Get weighted emotion probabilities for input text"""
    # Prepare input
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, padding=True)

    # Get predictions
    with torch.no_grad():
        outputs = model(**inputs)

    # Apply softmax to get probabilities
    probabilities = F.softmax(outputs.logits, dim=-1)

    # Convert to percentages
    percentages = probabilities[0].numpy() * 100

    return percentages


def main():
    # Load model and tokenizer
    model_path = os.path.join(current_dir, 'fine_tuned_emotion_model')
    model, tokenizer = load_model_and_tokenizer(model_path)

    # Define emotion labels
    emotion_mapping = {
        0: "Happy", 1: "Excited", 2: "Energetic", 3: "Fear",
        4: "Sad", 5: "Depressed", 6: "Calm", 7: "Angry"
    }

    # Get input from user
    while True:
        text = input("\nEnter text to analyze (or 'quit' to exit): ")
        if text.lower() == 'quit':
            break

        # Get emotion weights
        emotion_weights = get_emotion_weights(text, model, tokenizer)

        # Print results sorted by probability
        print("\nEmotion Distribution:")
        # Create list of (emotion, weight) tuples and sort by weight
        emotion_scores = [(emotion_mapping[i], weight)
                          for i, weight in enumerate(emotion_weights)]
        emotion_scores.sort(key=lambda x: x[1], reverse=True)

        # Print each emotion and its weight
        for emotion, weight in emotion_scores:
            print(f"{emotion}: {weight:.1f}%")


if __name__ == "__main__":
    main()
