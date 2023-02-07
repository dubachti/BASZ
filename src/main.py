from google.cloud import bigquery
import os
from bq_access import bq_push, bq_query
from housing_data import HousingData
from plotter import plot
from config import big_query_dir, path_to_ADC_json

    

def main():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path_to_ADC_json
    client = bigquery.Client()

    housingdata = HousingData(num_pages=30)
    housingdata.append_cycling_dist()
    bq_push(client, housingdata.df)

    query =    f'''
                SELECT  STREET as STREET,
                        ZIP_CODE as ZIP_CODE,
                        ROOMS as ROOMS,
                        CAST(SPACE as INT) as SPACE,
                        CAST(PRICE as INT) as PRICE,
                        CAST(CYCLE_TIME as INT) as CYCLE_TIME,
                        ROUND(CYCLE_DIST,1) as CYCLE_DISTANCE,
                        ROUND( POW(ROOMS/(SPACE),0.5) + POW(1/(CYCLE_DIST+CYCLE_TIME),0.5),2) AS SCORE
                FROM    `{big_query_dir}.housing.zurich_housing_data` 
                WHERE   ROOMS IS NOT NULL
                    AND PRICE IS NOT NULL
                    AND SPACE IS NOT NULL
                '''

    res = bq_query(client, query)
    plot(res)


if __name__ == '__main__': main()