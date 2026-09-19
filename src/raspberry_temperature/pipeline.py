#"""Construction of the master pipeline.
#"""
#
#from typing import Dict
#
#from kedro.pipeline import Pipeline
#
#from raspberry_temperature.pipelines.data_engineering import pipeline as de
#from raspberry_temperature.pipelines.data_engineering.nodes import log_running_time
#from raspberry_temperature.pipelines.data_sciences import pipeline as ds
#from raspberry_temperature.pipelines.share_data import pipeline as send_data
#
#def create_pipelines(**kwargs) -> Dict[str, Pipeline]:
#    """Create the project's pipeline.
#
#    Args:
#        kwargs: Ignore any additional arguments added in the future.
#
#    Returns:
#        A mapping from a pipeline name to a ``Pipeline`` object.
#
#    """
#    de_pipelines_dict = de.create_pipeline()
#    send_data_pipelines_dict = send_data.create_sending_data_pipeline()
#    de_pipeline = de_pipelines_dict['dev'].decorate(log_running_time)
#    de_pipeline_prod = de_pipelines_dict['prod'].decorate(log_running_time)
#    ds_training_pipeline = ds.create_training_pipeline().decorate(log_running_time)
#    send_data_pipeline_prod = send_data_pipelines_dict['prod'].decorate(log_running_time)
#    send_data_pipeline_pprd = send_data_pipelines_dict['pprd'].decorate(log_running_time)
#
#    return {
#        "de": de_pipeline,
#        "ds": ds_training_pipeline,
#        "prod": de_pipeline_prod + send_data_pipeline_prod,
#        "pprd": de_pipeline_prod + send_data_pipeline_pprd,
#        "__default__": de_pipeline + ds_training_pipeline,
#    }
#