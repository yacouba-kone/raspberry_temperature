from kedro.pipeline import Pipeline

from raspberry_temperature.pipelines.share_data import pipeline as share
from raspberry_temperature.pipelines.data_engineering import pipeline as de
from raspberry_temperature.pipelines.data_sciences import pipeline as ds 


def register_pipelines() -> dict[str, Pipeline]:

    data_engineering_dict = de.create_pipeline()
    send_data_pipelines_dict = share.create_sending_data_pipeline()
    de_pipeline = data_engineering_dict['dev']
    de_pipeline_prod = data_engineering_dict['prod']#.decorate(log_running_time)
    training_pipeline = ds.create_training_pipeline()
    send_data_pipeline_prod = send_data_pipelines_dict['prod']#.decorate(log_running_time)
    send_data_pipeline_pprd = send_data_pipelines_dict['pprd']#.decorate(log_running_time)


    return {
        "de": de_pipeline,
        "training": training_pipeline,
        "prod": de_pipeline_prod + send_data_pipeline_prod,
        "pprd": de_pipeline_prod + send_data_pipeline_pprd,
        "__default__": de_pipeline + training_pipeline,
    }

