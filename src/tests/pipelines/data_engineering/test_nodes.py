# ---------------------------------------------------------------------------
# Tests unitaires des nœuds de data engineering.
#
# Les tests suivent la convention « Given / When / Then » :
#   - Given  : jeu de données d'entrée et hypothèses ;
#   - When   : appel de la fonction testée ;
#   - Then   : comparaison avec le résultat attendu.
# ---------------------------------------------------------------------------

from raspberry_temperature.pipelines.data_engineering.nodes import clean_data, clean_data_prod
import pandas as pd
import numpy as np


def test_log_running_time():
    """Test de fumée : vérifie simplement que la suite de tests est exécutée."""
    assert True


def test_clean_data():
    """Vérifie que `clean_data` filtre les températures et ajoute le ratio."""
    # Given
    # Une observation à 31 °C (au-dessus du seuil de 30 °C)
    given_df = pd.DataFrame({
        "messageId": [1],
        "deviceId": ["Raspberry Pi Web Client"],
        "temperature": [31],
        "humidity": [66],
        "intensity": [66]
    })

    # When
    actual_df = clean_data(given_df)
    # Then
    # La ligne est conservée et la colonne `ratio` (66/66 = 1.0) est ajoutée
    expected_df = pd.DataFrame({
        "messageId": [1],
        "deviceId": ["Raspberry Pi Web Client"],
        "temperature": [31],
        "humidity": [66],
        "intensity": [66],
        "ratio": [1.0]
    })
    assert actual_df.equals(expected_df)


def test_clean_data_prod():
    """Vérifie `clean_data_prod` sur un message IoT typique d'Azure."""
    # Given
    # Message brut tel qu'envoyé par le Raspberry Pi (avec les métadonnées
    # ajoutées par Azure Event Hub / IoT Hub)
    given_df = [
        {
            "messageId": 1,
            "deviceId": "Raspberry Pi Web Client",
            "temperature": 31,
            "humidity": 66,
            "intensity": 66,
            "EventProcessedUtcTime": "2025-12-18T13:32:35.2140397Z",
            "PartitionId": 1,
            "EventEnqueuedUtcTime": "2025-12-18T13:32:15.2220000Z",
            "IoTHub": {
              "MessageId": "null",
              "CorrelationId": "null",
              "ConnectionDeviceId": "rasberry123",
              "ConnectionDeviceGenerationId": "638971735473123025",
              "EnqueuedTime": "2025-12-18T13:32:15.1570000Z"
            }
        }
    ]
    # When
    actual_df = clean_data_prod(given_df)
    print(actual_df)
    # Then
    # Seules les 5 colonnes utiles sont conservées, l'horodatage est converti en
    # datetime UTC et le ratio est calculé (66/66 = 1.0)
    expected_df = pd.DataFrame({
        "EventProcessedUtcTime": pd.to_datetime("2025-12-18T13:32:35.2140397Z", utc=True),
        "temperature": [31],
        "humidity": [66],
        "intensity": [66],
        "ratio": [1.0]
    })
    assert actual_df.equals(expected_df)