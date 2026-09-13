import logging
import pandas as pd
import pytest
from raspberry_temperature.pipelines.data_engineering.nodes import clean_data
logging.basicConfig(level=logging.INFO)


@pytest.fixture
def raspberry_data() -> pd.DataFrame:
    """
    Fixture containing sample Raspberry Pi temperature data.
    """
    return pd.DataFrame(
        {
            "temperature": [25, 30, 35, 40, 45],
            "intensity": [100, 120, 140, 160, 180],
            "humidity": [50, 60, 70, 80, 90],
        }
    )


def test_data_cleaning(raspberry_data: pd.DataFrame) -> None:
    """
    Test that clean_data:
    - removes rows where temperature < 30;
    - correctly calculates the ratio column.
    """

    # Clean the data
    cleaned_data = clean_data(raspberry_data)

    # Check that no temperature below 30 remains
    assert all(
        cleaned_data["temperature"] >= 30
    ), (
        "Data leakage detected: "
        "Rows with temperature < 30 are present."
    )

    # Check that the ratio is correctly calculated
    expected_ratios = (
        cleaned_data["intensity"]
        / cleaned_data["humidity"]
    )

    assert all(
        cleaned_data["ratio"] == expected_ratios
    ), (
        "Data leakage detected: "
        "Ratio column is incorrect."
    )
