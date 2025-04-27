import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import os

current_dir = os.path.dirname(os.path.abspath(__file__))


def evaluate_model(model_path, test_data_path):
    """
    Evaluate the model using test dataset
    """
    # Load model and tokenizer
    print("Loading model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()

    # Load test data
    print("Loading test data...")
    test_df = pd.read_csv(test_data_path)

    # Lists to store predictions and true labels
    all_predictions = []
    all_true_labels = []
    all_probabilities = []

    # Process each text in the test set
    print("Evaluating model...")
    for _, row in tqdm(test_df.iterrows(), total=len(test_df)):
        # Prepare input
        inputs = tokenizer(str(row['text']), return_tensors="pt",
                           truncation=True, padding=True)

        # Get predictions
        with torch.no_grad():
            outputs = model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_label = torch.argmax(outputs.logits).item()

        all_predictions.append(predicted_label)
        all_true_labels.append(row['label'])
        all_probabilities.append(probabilities[0].numpy())

    # Calculate metrics
    print("\nGenerating classification report...")
    emotion_mapping = {
        0: "Happy", 1: "Excited", 2: "Energetic", 3: "Fear",
        4: "Sad", 5: "Depressed", 6: "Calm", 7: "Angry"
    }

    report = classification_report(all_true_labels, all_predictions,
                                   target_names=list(emotion_mapping.values()),
                                   digits=3)

    # Generate confusion matrix
    print("Generating confusion matrix...")
    cm = confusion_matrix(all_true_labels, all_predictions)

    # Plot confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=list(emotion_mapping.values()),
                yticklabels=list(emotion_mapping.values()))
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Calculate and display additional metrics
    accuracy = np.mean(np.array(all_predictions) == np.array(all_true_labels))

    # Convert probabilities to numpy array for easier manipulation
    probabilities_array = np.array(all_probabilities)

    # Calculate average confidence scores
    avg_confidence = np.mean(
        [prob[pred] for prob, pred in zip(all_probabilities, all_predictions)])

    return {
        'classification_report': report,
        'accuracy': accuracy,
        'average_confidence': avg_confidence,
        'confusion_matrix': cm
    }


def main():
    # Set paths
    model_path = os.path.join(current_dir, 'fine_tuned_emotion_model')
    test_data_path = os.path.join(current_dir, 'data', 'test_dataset.csv')

    # Run evaluation
    try:
        results = evaluate_model(model_path, test_data_path)

        # Print results
        print("\n=== Model Evaluation Results ===")
        print(f"\nOverall Accuracy: {results['accuracy']:.3f}")
        print(
            f"Average Prediction Confidence: {results['average_confidence']:.3f}")
        print("\nDetailed Classification Report:")
        print(results['classification_report'])
        print("\nConfusion matrix has been saved as 'confusion_matrix.png'")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
