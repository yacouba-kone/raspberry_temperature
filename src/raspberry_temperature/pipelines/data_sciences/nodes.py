
import logging
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
import datetime
logging.basicConfig(level=logging.INFO)

def train_model(params: tuple, X_train:np.ndarray, y_train:np.ndarray) -> LinearRegression:
    """
    Train a linear regression model.

    Args:
        X_train (np.ndarray): Training features.
        y_train (np.ndarray): Training target.

    Returns:
        LinearRegression: Trained model.
    """
    model = LinearRegression(fit_intercept=params)#, normalize=params[1])
    model.fit(X_train, y_train)
    return model

def split_data(X:np.ndarray, y:np.ndarray, test_size:float=0.2, random_state:int=42):
    """
    Split the dataset into training and testing sets.

    Args:
        X (np.ndarray): Features.
        y (np.ndarray): Target.
        test_size (float): Proportion of the dataset to include in the test split.
        random_state (int): Random seed for reproducibility.

    Returns:
        tuple: Split data (X_train, X_test, y_train, y_test).
    """
    np.random.seed(random_state)
    indices = np.arange(X.shape[0])
    np.random.shuffle(indices)

    test_size = int(X.shape[0] * test_size)
    test_indices = indices[:test_size]
    train_indices = indices[test_size:]

    X_train, X_test = X[train_indices], X[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]

    return X_train, X_test, y_train, y_test


def scoring(model: LinearRegression, X_test:np.ndarray, y_test:np.ndarray) -> float:
    """
    Evaluate the model using R^2 score.

    Args:
        model (LinearRegression): Trained model.
        X_test (np.ndarray): Testing features.
        y_test (np.ndarray): Testing target.

    Returns:
        float: R^2 score of the model on the test set.
    """
    score = model.score(X_test, y_test)
    y_pred = model.predict(X_test)
    df_results = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
    df_results['Time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
    mse = np.mean((y_test - y_pred) ** 2)
    evs = 1 - (np.var(y_test - y_pred) / np.var(y_test))

    coefficients = None
    intercept = None

    try:
        if hasattr(model, 'coef_'):
            coefficients = model.coef_
        if hasattr(model, 'intercept_'):
            intercept = model.intercept_
    except Exception as e:
        logging.warning(f"Error occurred while extracting model parameters: {e}")
    logging.info(f"Model parameters - Coefficients: {coefficients}, Intercept: {intercept}")
    logging.info(f"Model evaluation metrics - R^2 Score: {score}, RMSE: {rmse}, MSE: {mse}, Explained Variance Score: {evs}")
    return {"r2_score": score, "rmse": rmse, "mse": mse, "explained_variance": evs,}


