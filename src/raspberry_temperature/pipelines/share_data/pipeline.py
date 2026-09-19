from kedro.pipeline import Pipeline, node

from .nodes import predict


def create_sending_data_pipeline(**kwargs):
    prod_pipeline = Pipeline(
        [
            node(
                predict,
                inputs=["model_temperature", "cleaned_data_prod", "params:features"],
                outputs="output_table_prod",
                name="send_prod_data"
            )
        ],
        tags=["send_data_prod"]
    )

    pprd_pipeline = Pipeline(
        [
            node(
                predict,
                inputs=["model_temperature", "cleaned_data_prod", "params:features"],
                outputs="output_table_pprd",
                name="send_pprd_data"
            )
        ],
        tags=["send_data_pprd"]
    )

    return {
        "prod": prod_pipeline,
        "pprd": pprd_pipeline
    }
