import random
from openai import AsyncOpenAI
from rasa_sdk import Action
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted
import requests
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Initialize OpenAI client
client = AsyncOpenAI(
    api_key="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"
)

# Load models
model_path = "fine_tuned_emotion_model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()  # Set to evaluation mode

emotion_mapping = {
    0: "Happy",
    1: "Excited",
    2: "Energetic",
    3: "Fear",
    4: "Sad",
    5: "Depressed",
    6: "Calm",
    7: "Angry"
}

class ActionGreetUser(Action):
    def name(self):
        return "action_greet_user"

    async def run(self, dispatcher, tracker, domain):
        greetings = [
            "Hi there, welcome to VibeSync! What's on your mind today?",
            "Hi there, welcome to VibeSync! What did you do today?",
            "Hi there, welcome to VibeSync! Let me know how I can help!",
            "Hi there, welcome to VibeSync! How's your day going so far?",
            "Hi there, welcome to VibeSync! How are you doing?",
            "Hi there, welcome to VibeSync! Anything interesting happened lately?",
            "Hi there, welcome to VibeSync! How's life been?",
            "Hi there, welcome to VibeSync! What's new with you?"
        ]
        dispatcher.utter_message(text=random.choice(greetings))
        return []

class ActionAnalyzeEmotionAndGenerateResponse(Action):
    def name(self):
        return "action_analyze_emotion_and_generate_response"

    async def run(self, dispatcher, tracker, domain):
        # Get current message
        user_message = tracker.latest_message.get("text", "")
        context_messages = []
        
        # Gather the last 3 user messages
        for event in reversed(tracker.events):
            if event.get("event") == "user" and event.get("text"):
                context_messages.append(event["text"])
                if len(context_messages) >= 5:  # Limit to the last 5 messages
                    break

        # Reverse to maintain the order of messages
        context_messages = list(reversed(context_messages))

        # Summarize the last 3 messages using OpenAI
        summary_prompt = (
            """Summarize the following messages in a concise and descriptive way, 
            while keeping the context and nuances of the messages.
            The summary is to help provide contextual awareness for the following messages.:\n"""
            f"{' '.join(context_messages)}"
        )

        try:
            summary_completion = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                        "content": "You are an assistant summarizing a conversation."},
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=250
            )
            summary = summary_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI Summarization Error: {e}")
            summary = "Unable to summarize previous messages."

        combined_input = f"{summary} {user_message}"

        print(f"\nUser message: {combined_input}")

        # Do emotion analysis
        inputs = tokenizer(combined_input, return_tensors="pt",
                           truncation=True, padding=True)

        # Use torch.no_grad() for inference
        with torch.no_grad():
            outputs = model(**inputs)
            # Use F.softmax instead of torch.softmax
            probabilities = F.softmax(outputs.logits, dim=-1)
            # Convert to numpy array
            probabilities = probabilities[0].numpy()

        # Calculate emotion weights (as decimals)
        weighted_emotions = {
            emotion_mapping[i]: float(probabilities[i])
            for i in range(len(probabilities))
        }

        # Sort emotions by weight for display
        sorted_emotions = sorted(
            weighted_emotions.items(), key=lambda x: x[1], reverse=True)
        emotion_display = "\nEmotion Analysis:\n" + "\n".join([
            f"{emotion}: {weight:.4f}"
            for emotion, weight in sorted_emotions
        ])
        print(emotion_display)
        
        # Send emotions to Flask API
        try:
            response = requests.post(
                "http://localhost:5006/update_emotions", json=weighted_emotions)
            if response.status_code == 200:
                print("Emotions sent successfully.")
        except Exception as e:
            print(f"Error sending emotions: {e}")

        try:
            # Generate conversational response
            completion = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a VibeSync chatbot. VibeSync is an emotion based music recommendation system.
                     Your goal is to have a conversation with the user to detect their mood. You are a friendly chatbot having a natural conversation. 
                     Respond naturally to continue the conversation, and match the users length and talking style. Explore on the users responses and continue the natural flow of the conversation.
                     Be engaging but concise. Don't mention emotions explicitly unless the user brings them up."""},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000
            )

            response = completion.choices[0].message.content

            # Send both the chatbot response and emotion analysis
            dispatcher.utter_message(text=f"{response}")

            return [SlotSet("weighted_emotions", weighted_emotions)]

        except Exception as e:
            print(f"Error generating response: {e}")
            dispatcher.utter_message(
                text=f"I'm having trouble responding, but here are your emotion weights:\n{emotion_display}")
            return []
