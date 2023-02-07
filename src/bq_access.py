import pandas as pd
from google.cloud import bigquery
from housing_data import STREET, ZIP, ROOMS, SPACE, PRICE, CYCLE_TIME, CYCLE_DIST

# submit df to bigquery
def bq_push(client: bigquery.Client,df: pd.DataFrame) -> None:
    schema = [
    bigquery.SchemaField(STREET, 'STRING'),
    bigquery.SchemaField(ZIP, 'INTEGER'),
    bigquery.SchemaField(ROOMS, 'FLOAT'),
    bigquery.SchemaField(SPACE, 'FLOAT'),
    bigquery.SchemaField(PRICE, 'FLOAT'),
    bigquery.SchemaField(CYCLE_TIME, 'FLOAT'),
    bigquery.SchemaField(CYCLE_DIST, 'FLOAT'),
    ]

    if not client.get_dataset('housing'):
        client.create_dataset('housing')
    table_ref = client.dataset('housing')
    table_id = table_ref.table(table_id)

    job_config = bigquery.LoadJobConfig()
    job_config.create_disposition='CREATE_IF_NEEDED'
    job_config.write_disposition='WRITE_TRUNCATE'
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.schema = schema

    job = client.load_table_from_dataframe( df,
                                            'zurich_housing_data',
                                            location='US',
                                            job_config=job_config)
    
    job.result()
    print('data succesfully submitted to bq housing dataset')

# query df on bigquery
def bq_query(client: bigquery.Client, query: str) -> pd.DataFrame:
    try:
        return client.query(query).to_dataframe()
    except:
        raise ConnectionError('Could not connect to BigQuery')