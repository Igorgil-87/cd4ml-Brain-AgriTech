# cd4ml_pipeline/sensors/slack_sensors.py

from dagster import RunStatus, SensorEvaluationContext, run_status_sensor
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

SLACK_TOKEN = os.getenv("SLACK_API_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#alertas-dagster")

@run_status_sensor(
    run_status=RunStatus.FAILURE,
    name="notify_on_failure",
)
def notify_on_failure(context: SensorEvaluationContext):
    if context.pipeline_run:
        message = f":rotating_light: Pipeline *{context.pipeline_run.pipeline_name}* falhou! Run ID: {context.pipeline_run.run_id}"
        
        client = WebClient(token=SLACK_TOKEN)
        try:
            client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
        except SlackApiError as e:
            context.log.error(f"Erro ao enviar mensagem Slack: {e.response['error']}")