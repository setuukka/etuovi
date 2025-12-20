from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime

default_args = {
    "owner": "tuukka",
    "depends_on_past": False,
    "start_date": datetime(2025, 12, 20),
    "retries": 0,
}

with DAG(
    dag_id="etuovi_scraper_dag",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    get_listings = DockerOperator(
        task_id="get_listings",
        image="etuovi-scrape",
        api_version="auto",
        auto_remove=True,
        command="scripts/get_listings.py 'https://www.etuovi.com/myytavat-asunnot/oulu/rajakyla?haku=M2379748132'",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        mounts=[],
    )
