from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import GridSearchCV
from raspberry_temperature.pipelines.data_sciences.nodes import train_model, split_data, scoring
from raspberry_temperature.pipelines.data_engineering.pipeline import workflow_engineering
import numpy as np
import pandas as pd
import os
import logging
from pathlib import Path
import mlflow
import datetime
import seaborn as sns

def workflow_sciences(file_path: Path) -> None:
    print("Starting process for raspberry-temperature!")
    
     # --------------------------------------------------
    # MLflow configuration
    # --------------------------------------------------
    mlflow.set_tracking_uri( "http://127.0.0.1:5000")
    mlflow.set_experiment("raspberry-temperature")

    # --------------------------------------------------
    # Data engineering
    # --------------------------------------------------
    cleaned_data = workflow_engineering(file_path)

    # --------------------------------------------------
    # Features / target
    # --------------------------------------------------
    X = cleaned_data[["intensity", "humidity", "ratio"]].values
    y = cleaned_data["temperature"].values

    # --------------------------------------------------
    # Parameters
    # --------------------------------------------------
    test_size = 0.2
    random_state = 42

    # --------------------------------------------------
    # MLflow run
    # --------------------------------------------------
    run_name = f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with mlflow.start_run(run_name=run_name):

        # Log parameters
        mlflow.log_param("test_size",test_size)
        mlflow.log_param("random_state",random_state)
        mlflow.log_param("model_type","LinearRegression")

        # --------------------------------------------------
        # Split
        # --------------------------------------------------
        X_train, X_test, y_train, y_test = split_data(X,y,test_size=test_size,random_state=random_state,)

        #--------------------------------------------------
        # Tuning hyperparameters (if any)
        # --------------------------------------------------
        search_space = {
            "fit_intercept": [True, False],
        }
        search = GridSearchCV(LinearRegression(), search_space, cv=5)
        search.fit(X_train, y_train)

        best_model = search.best_estimator_
        best_params = search.best_params_["fit_intercept"]#, search.best_params_["normalize"]

        #--------------------------------------------------
        # Log best parameters       
        # --------------------------------------------------
        mlflow.log_param("best_fit_intercept", best_params)
        # mlflow.log_param("best_normalize", best_params[1])

        # Train
        # --------------------------------------------------
        model = train_model(best_params,X_train,y_train)

        # --------------------------------------------------
        # Evaluation
        # --------------------------------------------------
        score = scoring(model,X_test,y_test)

        #--------------------------------------------------
        # Residual analysis
        # --------------------------------------------------
        y_pred = model.predict(X_test)
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
        mlflow.log_metric("r2_score",score["r2_score"])
        mlflow.log_metric("rmse",score["rmse"])
        mlflow.log_metric("mse",score["mse"])
        mlflow.log_metric("explained_variance",score["explained_variance"])

        # --------------------------------------------------
        # Log model
        # --------------------------------------------------
        mlflow.sklearn.log_model(model,name="model")

        print( f"Model R² score: {score}")

        print('Artifcats URL:', mlflow.get_artifact_uri())


if __name__ == "__main__":

    ROOT_DIR = Path(__file__).resolve().parents[4]

    file_path = (ROOT_DIR/ "data"/ "raw"/ "IntroMLops-1.json")
    workflow_sciences(file_path)
    