
import logging
from typing import List
import mlflow
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from sklearn.model_selection import GridSearchCV
logging.basicConfig(level=logging.INFO)


def split_data(features_data: pd.DataFrame, features: List, label_name: List,test_size:float=0.2, random_state:int=42) -> List:
    """
    Split the dataset into training and testing sets.

    Args:
        features_data (pd.DataFrame): The input features data.
        features (List): List of feature column names.
        label_name (List): List of label column names.

    Returns:
        List: A list containing the split data: [X_train, X_test, y_train, y_test].
    """
    X = features_data[features].values
    y = features_data[label_name].values

    np.random.seed(random_state)
    indices = np.arange(X.shape[0])
    np.random.shuffle(indices)

    test_size = int(X.shape[0] * test_size)
    test_indices = indices[:test_size]
    train_indices = indices[test_size:]

    X_train, X_test = X[train_indices], X[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]

    return (
        pd.DataFrame(X_train, columns=features),
        pd.DataFrame(X_test, columns=features),
        pd.DataFrame(y_train, columns=[label_name]),
        pd.DataFrame(y_test, columns=[label_name]),
    )#X_train, X_test, y_train, y_test


def predict(model: "LinearRegression", X_test:pd.DataFrame, y_test:pd.DataFrame) -> float:
    """
    Evaluate the model using R^2 score.

    Args:
        model (LinearRegression): Trained model.
        X_test (pd.DataFrame): Testing features.
        y_test (pd.DataFrame): Testing target.

    Returns:
        float: R^2 score of the model on the test set.
    """
    log = logging.getLogger(__name__)
    
    x_test = X_test.to_numpy()
    y_test = y_test.to_numpy().ravel()
    score = model.score(X_test, y_test)
    y_pred = model.predict(X_test)
    df_results = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
    df_results['Time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return df_results#,{"r2_score": score, "rmse": rmse, "mse": mse, "explained_variance": evs,}


def train_model(X_train:pd.DataFrame, X_test:pd.DataFrame, y_train:pd.DataFrame, y_test:pd.DataFrame) -> LinearRegression:
    """
    Train a linear regression model.

    Args:
        X_train (pd.DataFrame): Training features.
        y_train (pd.DataFrame): Training target.

    Returns:
        LinearRegression: Trained model.
    """
    x_train = X_train.to_numpy()
    x_test = X_test.to_numpy()
    y_train = y_train.to_numpy().ravel()
    y_test = y_test.to_numpy().ravel()

    mlflow.set_tracking_uri( "http://127.0.0.1:5000")
    mlflow.set_experiment("raspberry-temperature")

    # --------------------------------------------------
    # MLflow run
    # --------------------------------------------------
    run_name = f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with mlflow.start_run(run_name=run_name):

        # Log parameters
        #mlflow.log_param("test_size",test_size)
        #mlflow.log_param("random_state",random_state)
        mlflow.log_param("model_type","LinearRegression")

        #--------------------------------------------------
        # Tuning hyperparameters (if any)
        # --------------------------------------------------
        search_space = {
            "fit_intercept": [True, False],
        }
        search = GridSearchCV(LinearRegression(), search_space, cv=5)
        search.fit(x_train, y_train)

        best_model = search.best_estimator_
        best_params = search.best_params_["fit_intercept"]#, search.best_params_["normalize"]

        #--------------------------------------------------
        # Log best parameters       
        # --------------------------------------------------
        mlflow.log_param("best_fit_intercept", best_params)
        # mlflow.log_param("best_normalize", best_params[1])

        # Train
        # --------------------------------------------------
        model = LinearRegression()
        model.fit(x_train, y_train)

        # --------------------------------------------------
        # Evaluation
        # --------------------------------------------------
        score = model.score(X_test, y_test)
        y_pred = model.predict(X_test)

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

        #--------------------------------------------------
        # Residual analysis
        # --------------------------------------------------
        #y_pred = model.predict(x_test)
        residuals = y_test - y_pred 
        fig_residuals, ax_residuals = plt.subplots(figsize=(8, 6))
        sns.histplot(residuals, kde=True)
        ax_residuals.axhline(y=0, color='r', linestyle='--')
        ax_residuals.set_xlabel('Predicted Values')
        ax_residuals.set_ylabel('Residuals')
        ax_residuals.set_title('Residual Analysis')
        plt.savefig("residual_analysis.png")
        plt.close()

        fig_results, ax_results = plt.subplots(figsize=(8, 6))
        ax_results.scatter(y_test, y_pred)
        ax_results.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        ax_results.set_xlabel('Actual Values')
        ax_results.set_ylabel('Predicted Values')
        ax_results.set_title('Actual vs Predicted Values')
        plt.savefig("actual_vs_predicted.png")
        plt.close()

        mlflow.log_figure(fig_residuals, "plots/residual_analysis.png")
        mlflow.log_figure(fig_results, "plots/actual_vs_predicted.png")

        # Log metrics
        # --------------------------------------------------
        mlflow.log_metric("r2_score",score)
        mlflow.log_metric("rmse",rmse)
        mlflow.log_metric("mse",mse)
        mlflow.log_metric("explained_variance",evs)

        # --------------------------------------------------
        # Log model
        # --------------------------------------------------
        mlflow.sklearn.log_model(model,name="model")

        print( f"Model R² score: {score}")

        print('Artifcats URL:', mlflow.get_artifact_uri())
        #model = LinearRegression(fit_intercept=params)#, normalize=params[1])
        #model.fit(X_train, y_train)
    return model


def make_scatter(regressor: LinearRegression, x_test: np.ndarray, y_test: np.ndarray):
    fig, ax = plt.subplots()
    y_pred = regressor.predict(x_test)
    plt.scatter(y_test, y_pred)
    plt.plot([0, 80], [0, 80], '--k', lw=3, c='red')
    plt.axis('tight')
    plt.xlabel('Temperature du jus froid')
    plt.ylabel('Temperature du jus froid prédicte')
    fig.savefig('plot.png')
    fig.set_size_inches(12, 12)
    return fig

