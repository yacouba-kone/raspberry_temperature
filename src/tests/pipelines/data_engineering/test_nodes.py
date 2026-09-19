from raspberry_temperature.pipelines.data_engineering.nodes import clean_data, clean_data_prod
import pandas as pd
import numpy as np


def test_log_running_time():
    assert True


def test_clean_data():
    # Given
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
    # Given
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
    expected_df = pd.DataFrame({
        "EventProcessedUtcTime": pd.to_datetime("2025-12-18T13:32:35.2140397Z", utc=True),
        "temperature": [31],
        "humidity": [66],
        "intensity": [66],
        "ratio": [1.0]
    })
    assert actual_df.equals(expected_df)