import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

class ArousalPredictor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        self.features = [
            'Sp_Duration_ms', 'Sp_Danceability', 'Sp_Energy',
            'Sp_Loudness', 'Sp_Speechiness', 'Sp_Acousticness',
            'Sp_Instrumentalness', 'Sp_Liveness', 'Sp_Valence', 'Sp_Tempo', 'Sp_SpeechRate'
        ]
        self.is_fitted = False
        self.train_residuals = None
        self.train_predictions = None
        self.feature_importance = None

    # Fit the arousal prediction model and visualize results
    def fit(self, data_path):
        df = pd.read_csv(data_path)

        # Split features and target
        X = df[self.features]
        y = df['Avg_Arousal']

        # Split into train-test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42)

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train the model
        print("\nFitting XGBoost Model...")
        self.model.fit(X_train_scaled, y_train)
        self.train_predictions = self.model.predict(X_train_scaled)
        self.train_residuals = y_train - self.train_predictions

        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        self._evaluate_model(y_test, y_pred)

        # Calculate feature importance
        self.calculate_feature_importance()

        self.is_fitted = True

        # Visualizations
        self.plot_training_data_and_fit(X_train_scaled, y_train)
        self.plot_residuals()
        self.plot_feature_importance()
        self.analyze_predictions(X_test_scaled, y_test)

    # Calculate feature importance using XGBoost
    def calculate_feature_importance(self):
        self.feature_importance = pd.DataFrame({
            'feature': self.features,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

    # Visualize training data: Predicted vs Actual
    def plot_training_data_and_fit(self, X_train, y_train):
        plt.figure(figsize=(12, 8))
        predictions = self.model.predict(X_train)
        plt.scatter(predictions, y_train, alpha=0.5,
                    label='Training Data', color='blue')
        plt.plot([y_train.min(), y_train.max()], [y_train.min(),
                 y_train.max()], 'r--', label='Perfect Fit')
        plt.xlabel('Predicted Arousal')
        plt.ylabel('Actual Arousal')
        plt.title('Training Data: Predicted vs Actual')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    # Visualize residuals analysis
    def plot_residuals(self):
        if not self.is_fitted:
            raise ValueError(
                "The model must be fitted before visualizing residuals.")

        fig, axes = plt.subplots(1, 2, figsize=(15, 5))

        # Residuals vs Fitted
        axes[0].scatter(self.train_predictions,
                        self.train_residuals, alpha=0.5, label='Residuals')
        axes[0].axhline(0, color='r', linestyle='--', label='Zero Line')
        axes[0].set_xlabel('Fitted Values')
        axes[0].set_ylabel('Residuals')
        axes[0].set_title('Residuals vs Fitted')
        axes[0].legend()

        # Residuals Distribution
        sns.histplot(self.train_residuals, kde=True, ax=axes[1])
        axes[1].set_title('Residuals Distribution')
        axes[1].set_xlabel('Residuals')

        plt.tight_layout()
        plt.show()

    # Visualize feature importance
    def plot_feature_importance(self):
        plt.figure(figsize=(12, 6))
        sns.barplot(
            data=self.feature_importance,
            x='importance',
            y='feature',
            palette='viridis'
        )
        plt.title('Feature Importance for Arousal Prediction')
        plt.xlabel('Importance Score')
        plt.ylabel('Feature')
        plt.tight_layout()
        plt.show()

    # Analyze and visualize predictions on test data
    def analyze_predictions(self, X_test_scaled, y_test):
        predictions = self.model.predict(X_test_scaled)

        # Scatter plot: Actual vs Predicted
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, predictions, alpha=0.5, label='Test Data')
        plt.plot([y_test.min(), y_test.max()], [y_test.min(),
                 y_test.max()], 'r--', label='Perfect Fit')
        plt.xlabel('Actual Arousal')
        plt.ylabel('Predicted Arousal')
        plt.title('Test Data: Actual vs Predicted Arousal')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    # Evaluate and display model performance metrics
    def _evaluate_model(self, y_test, y_pred):
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)

        print("\nModel Performance:")
        print(f"R² Score: {r2:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"MAE: {mae:.4f}")

predictor = ArousalPredictor()
predictor.fit(os.path.join(current_dir, 'Datasets', 'MER_spotify_dataset.csv'))

# Save the scaler and trained model
joblib.dump(predictor.scaler, os.path.join(current_dir, 'Models', 'arousal_scaler.pkl'))
joblib.dump(predictor.model, os.path.join(current_dir, 'Models', 'arousal_model.pkl'))
print("Trained arousal scaler and model saved")
