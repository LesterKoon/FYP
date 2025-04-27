import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
from sklearn.feature_selection import f_regression
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, explained_variance_score
import warnings
import os

warnings.filterwarnings('ignore')

current_dir = os.path.dirname(os.path.abspath(__file__))

# Calculate evaluation metrics
def calculate_metrics(y_true, y_pred):
    return {
        'r2': r2_score(y_true, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'mae': mean_absolute_error(y_true, y_pred),
        'explained_variance': explained_variance_score(y_true, y_pred)
    }

# Rank models and select the best model
def select_best_model(results):
    df_results = pd.DataFrame(results).T

    rankings = pd.DataFrame(index=df_results.index)

    higher_better = ['r2', 'cv_mean', 'explained_variance']
    lower_better = ['rmse', 'mae', 'cv_std']

    # Rank metrics
    for metric in higher_better:
        rankings[f'{metric}_rank'] = df_results[metric].rank(ascending=False)

    for metric in lower_better:
        rankings[f'{metric}_rank'] = df_results[metric].rank(ascending=True)

    # Calculate average rank
    rankings['avg_rank'] = rankings.mean(axis=1)
    scores = pd.DataFrame(index=df_results.index)

    for metric in higher_better:
        min_val = df_results[metric].min()
        max_val = df_results[metric].max()
        scores[metric] = 100 * (df_results[metric] -
                                min_val) / (max_val - min_val)

    for metric in lower_better:
        min_val = df_results[metric].min()
        max_val = df_results[metric].max()
        scores[metric] = 100 * \
            (max_val - df_results[metric]) / (max_val - min_val)

    weights = {
        'r2': 0.25,
        'rmse': 0.20,
        'mae': 0.15,
        'cv_mean': 0.20,
        'cv_std': 0.10,
        'explained_variance': 0.10
    }

    scores['overall_score'] = sum(
        scores[metric] * weight for metric, weight in weights.items())

    final_results = pd.DataFrame(index=df_results.index)

    for metric in df_results.columns:
        final_results[f'{metric}'] = df_results[metric].round(4)

    final_results['avg_rank'] = rankings['avg_rank'].round(2)
    final_results['overall_score'] = scores['overall_score'].round(2)

    # Sort by overall score
    final_results = final_results.sort_values('overall_score', ascending=False)
    final_results.insert(0, 'position', range(1, len(final_results) + 1))

    # Select the best model
    best_model = final_results.index[0]

    return final_results, best_model

#  Visualize model comparison
def plot_model_comparison(results):
    metrics = ['r2', 'rmse', 'mae', 'cv_mean']
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.ravel()

    for i, metric in enumerate(metrics):
        data = pd.DataFrame(results).T[metric]
        sns.barplot(x=data.index, y=data.values, ax=axes[i])
        axes[i].set_title(f'Model Comparison - {metric.upper()}')
        axes[i].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()

#  Analyze predictions
def analyze_predictions(model, X_test_scaled, y_test):
    predictions = model.predict(X_test_scaled)

    # Scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, predictions, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    plt.xlabel('Actual Arousal')
    plt.ylabel('Predicted Arousal')
    plt.title('Actual vs Predicted Arousal')
    plt.tight_layout()
    plt.show()

    # Error distribution
    errors = y_test - predictions
    plt.figure(figsize=(10, 6))
    sns.histplot(errors, kde=True)
    plt.title('Prediction Error Distribution')
    plt.xlabel('Prediction Error')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.show()


def main(data_path):
    # Load data
    df = pd.read_csv(data_path)

    features = [
        'Sp_Duration_ms', 'Sp_Danceability', 'Sp_Energy',
        'Sp_Loudness', 'Sp_Speechiness', 'Sp_Acousticness',
        'Sp_Instrumentalness', 'Sp_Liveness', 'Sp_Valence', 'Sp_Tempo', 'Sp_SpeechRate'
    ]
    X = df[features]
    y = df['Avg_Arousal']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42)

    # Feature scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Model dictionary
    models = {
        'Linear Regression': LinearRegression(),
        'Lasso': Lasso(alpha=0.1),
        'Ridge': Ridge(alpha=0.1),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42),
        'CatBoost': CatBoostRegressor(iterations=100, learning_rate=0.1, depth=6, random_seed=42, verbose=False),
        'SVR': SVR(kernel='rbf', C=1.0, epsilon=0.1)
    }

    results = {}
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)

        metrics = calculate_metrics(y_test, y_pred)
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)

        results[name] = {
            **metrics,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }

    ranking_results, best_model = select_best_model(results)
    pd.set_option('display.max_columns', None) 
    print("\nModel Rankings:")
    print(ranking_results)
    print(f"\nBest Model: {best_model}")

    # Fit the best model
    final_model = models[best_model]
    final_model.fit(X_train_scaled, y_train)

    # Visualizations
    analyze_predictions(final_model, X_test_scaled, y_test)
    plot_model_comparison(results)


if __name__ == "__main__":
    main(os.path.join(current_dir, 'Datasets', 'MER_spotify_dataset.csv'))
