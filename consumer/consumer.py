# Basic imports
from azure.eventhub import EventHubConsumerClient
import sys
import os 
from consumer_logger import logger
# Import conf of message_broker
from consumer_conf import CONNECTION_STR, CONSUMER_GROUP, EVENT_HUB_NAME



# configure workers
sys.path.append('..')
from celery_workers.tasks import process_message_with_kedro

# Define callbacks to process events
# We'll treat one event at a time
def on_event(partition_context, event):
    logger.info("Received event from partition: {}.".format(partition_context.partition_id))
    event_body = event.body_as_str()
    logger.info(f"Event received: {event_body}" )
    logger.info("Sending event to workers queue")
    process_message_with_kedro.delay(event_body)
    logger.info('Event sent to workers queue')
    #partition_context.update_checkpoint()

def on_error(partition_context, error):
    # Put your code here. partition_context can be None in the on_error callback.
    if partition_context:
        logger.error("An exception: {} occurred during receiving from Partition: {}.".format(
            partition_context.partition_id,
            error
        ))
    else:
        logger.error("An exception: {} occurred during the load balance process.".format(error))


#def on_event(partition_context, event):
#    logger.info(
#        "EVENT RECEIVED | partition=%s | offset=%s | sequence=%s",
#        partition_context.partition_id,
#        event.offset,
#        event.sequence_number,
#    )
#
#    try:
#        parts = list(event.body)
#
#        logger.info("BODY PARTS = %r", parts)
#        logger.info("BODY PART TYPES = %s", [type(x) for x in parts])
#
#    except Exception:
#        logger.exception("Erreur lecture body")

#def on_error(partition_context, error):
#    logger.error(
#        "ERREUR Event Hub | partition=%s | error=%s",
#        partition_context.partition_id if partition_context else None,
#        error,
#        exc_info=True,
#    )


def main():
    logger.info('Preparing receiving')
    client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group=CONSUMER_GROUP,
        eventhub_name=EVENT_HUB_NAME
    )
    logger.info('Connection to Azure Event Hub set')
    #with client:
    #    logger.info('Started receiving')
    #    client.receive(
    #        on_event=on_event,
    #        on_error=on_error,
    #        starting_position="@latest",
    #    )
    try:
        with client:
            logger.info('Started receiving')
            client.receive(
                on_event=on_event,
                on_error=on_error,
                starting_position='@latest'#"@latest"
            )
    except KeyboardInterrupt:
        logger.info("Receiving has stopped.")

if __name__ == '__main__':
    main()
