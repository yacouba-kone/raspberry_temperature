
# ---------------------------------------------------------------------------
# Nœuds (fonctions métier) du pipeline de data sciences.
#
# Enchaînement réalisé par le pipeline :
#   split_data  -> train_model -> predict
# Chaque entraînement est tracé dans MLflow (serveur local 127.0.0.1:5000).
# ---------------------------------------------------------------------------

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
    # Sélection des variables explicatives (X) et de la variable cible (y)
    X = features_data[features].values
    y = features_data[label_name].values

    # Mélange aléatoire des indices (reproductible grâce à random_state)
    np.random.seed(random_state)
    indices = np.arange(X.shape[0])
    np.random.shuffle(indices)

    # Découpage : les `test_size` premiers indices mélangés forment le jeu de test
    test_size = int(X.shape[0] * test_size)
    test_indices = indices[:test_size]
    train_indices = indices[test_size:]

    X_train, X_test = X[train_indices], X[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]

    # Les quatre jeux sont retournés sous forme de DataFrames nommés
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
    # NB : la docstring historique annonce un score R², mais la fonction retourne
    # en réalité un DataFrame contenant les valeurs réelles, les prédictions et
    # l'horodatage (type de retour réel : pd.DataFrame).
    log = logging.getLogger(__name__)

    # `x_test` n'est pas réutilisé ensuite (les conversions servent surtout à
    # `y_test`) mais l'appel est conservé tel quel
    x_test = X_test.to_numpy()
    y_test = y_test.to_numpy().ravel()
    # Score R² du modèle sur le jeu de test (calculé pour information)
    score = model.score(X_test, y_test)
    # Prédictions du modèle sur le même jeu de test
    y_pred = model.predict(X_test)
    df_results = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
    # Horodatage de la prédiction : colonne `Time` attendue par la table SQL
    df_results['Time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return df_results#,{"r2_score": score, "rmse": rmse, "mse": mse, "explained_variance": evs,}


def train_model(X_train:pd.DataFrame, X_test:pd.DataFrame, y_train:pd.DataFrame, y_test:pd.DataFrame) -> LinearRegression:
    """
    Train a linear regression model.

    Le suivi de l'expérience (paramètres, métriques, graphiques et modèle) est
    enregistré dans MLflow. Le modèle est entraîné sur le jeu d'entraînement
    après une recherche d'hyperparamètre, puis évalué sur le jeu de test.

    Args:
        X_train (pd.DataFrame): Training features.
        X_test (pd.DataFrame): Testing features.
        y_train (pd.DataFrame): Training target.
        y_test (pd.DataFrame): Testing target.

    Returns:
        LinearRegression: Trained model.
    """
    # Conversion des DataFrames en tableaux NumPy attendus par scikit-learn
    x_train = X_train.to_numpy()
    x_test = X_test.to_numpy()
    y_train = y_train.to_numpy().ravel()
    y_test = y_test.to_numpy().ravel()

    # Configuration de MLflow : serveur de suivi local + nom de l'expérience
    mlflow.set_tracking_uri( "http://127.0.0.1:5000")
    mlflow.set_experiment("raspberry-temperature")

    # --------------------------------------------------
    # MLflow run
    # --------------------------------------------------
    # Un « run » MLflow par entraînement, nommé avec la date et l'heure
    run_name = f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with mlflow.start_run(run_name=run_name):

        # Log parameters
        # (les paramètres de découpage ont été commentés : ils ne sont pas
        # disponibles dans cette fonction)
        #mlflow.log_param("test_size",test_size)
        #mlflow.log_param("random_state",random_state)
        mlflow.log_param("model_type","LinearRegression")

        #--------------------------------------------------
        # Tuning hyperparameters (if any)
        # --------------------------------------------------
        # Recherche du meilleur `fit_intercept` par validation croisée (5 folds)
        search_space = {
            "fit_intercept": [True, False],
        }
        search = GridSearchCV(LinearRegression(), search_space, cv=5)
        search.fit(x_train, y_train)

        # Meilleur estimateur et meilleure valeur de `fit_intercept` trouvés
        best_model = search.best_estimator_
        best_params = search.best_params_["fit_intercept"]#, search.best_params_["normalize"]

        #--------------------------------------------------
        # Log best parameters       
        # --------------------------------------------------
        # Journalisation du meilleur hyperparamètre dans MLflow
        mlflow.log_param("best_fit_intercept", best_params)
        # mlflow.log_param("best_normalize", best_params[1])

        # Train
        # --------------------------------------------------
        # NB : `best_model` (issu de GridSearchCV) n'est pas réutilisé :
        # un modèle neuf est entraîné avec les réglages par défaut
        model = LinearRegression()
        model.fit(x_train, y_train)

        # --------------------------------------------------
        # Evaluation
        # --------------------------------------------------
        # NB : `X_test` reste un DataFrame tandis que `y_test` a été converti en
        # tableau NumPy plus haut ; scikit-learn accepte les deux formats
        score = model.score(X_test, y_test)
        y_pred = model.predict(X_test)

        # Métriques d'erreur calculées manuellement
        rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
        mse = np.mean((y_test - y_pred) ** 2)
        evs = 1 - (np.var(y_test - y_pred) / np.var(y_test))

        # Paramètres appris par le modèle (pente et ordonnée à l'origine)
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
        # Graphique 1 : distribution des résidus (avec estimation de densité)
        fig_residuals, ax_residuals = plt.subplots(figsize=(8, 6))
        sns.histplot(residuals, kde=True)
        ax_residuals.axhline(y=0, color='r', linestyle='--')
        ax_residuals.set_xlabel('Predicted Values')
        ax_residuals.set_ylabel('Residuals')
        ax_residuals.set_title('Residual Analysis')
        # Sauvegarde locale du graphique puis libération de la figure
        plt.savefig("residual_analysis.png")
        plt.close()

        # Graphique 2 : valeurs réelles vs valeurs prédites (droite y = x)
        fig_results, ax_results = plt.subplots(figsize=(8, 6))
        ax_results.scatter(y_test, y_pred)
        ax_results.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        ax_results.set_xlabel('Actual Values')
        ax_results.set_ylabel('Predicted Values')
        ax_results.set_title('Actual vs Predicted Values')
        plt.savefig("actual_vs_predicted.png")
        plt.close()

        # Les deux figures sont aussi enregistrées comme artefacts MLflow
        mlflow.log_figure(fig_residuals, "plots/residual_analysis.png")
        mlflow.log_figure(fig_results, "plots/actual_vs_predicted.png")

        # Log metrics
        # --------------------------------------------------
        # Journalisation des métriques d'évaluation dans MLflow
        mlflow.log_metric("r2_score",score)
        mlflow.log_metric("rmse",rmse)
        mlflow.log_metric("mse",mse)
        mlflow.log_metric("explained_variance",evs)

        # --------------------------------------------------
        # Log model
        # --------------------------------------------------
        # Sérialisation du modèle entraîné comme artefact MLflow
        mlflow.sklearn.log_model(model,name="model")

        print( f"Model R² score: {score}")

        print('Artifcats URL:', mlflow.get_artifact_uri())
        # Ancienne initialisation du modèle avec les hyperparamètres trouvés
        #model = LinearRegression(fit_intercept=params)#, normalize=params[1])
        #model.fit(X_train, y_train)
    # Le modèle est retourné pour être persisté par Kedro (dataset
    # `model_temperature`, cf. catalog.yml)
    return model


def make_scatter(regressor: LinearRegression, x_test: np.ndarray, y_test: np.ndarray):
    """Trace un nuage de points « température réelle vs température prédite ».

    Fonction utilitaire conservée pour des analyses ponctuelles : elle
    enregistre le graphique dans `plot.png` et retourne la figure matplotlib.

    Args:
        regressor: modèle entraîné.
        x_test: variables explicatives de test.
        y_test: températures réelles de test.
    """
    fig, ax = plt.subplots()
    y_pred = regressor.predict(x_test)
    plt.scatter(y_test, y_pred)
    # Droite de référence y = x : une prédiction parfaite s'y superpose
    plt.plot([0, 80], [0, 80], '--k', lw=3, c='red')
    plt.axis('tight')
    plt.xlabel('Temperature du jus froid')
    plt.ylabel('Temperature du jus froid prédicte')
    # NB : la taille de la figure est modifiée après la sauvegarde, le fichier
    # `plot.png` est donc exporté en 6x4 pouces (taille par défaut de Matplotlib)
    fig.savefig('plot.png')
    fig.set_size_inches(12, 12)
    return fig

