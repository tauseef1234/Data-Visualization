# Chicago crime data visualization

This interactive dashboard maps the city of Chicago by offence count for the year 2019. The dashboard shows a choropleth map of the city of Chicago that hads counties color coded by the offence count, a datatable and a horizontal bar chart of the offence types.


## Input Data

The source data for this dashboard is extracted from [Google cloud public dataset](https://console.cloud.google.com/marketplace/product/city-of-chicago-public-data/chicago-crime?filter=solution-type:dataset&id=a985ccaf-0a3a-4eb9-a2de-c4fd07de08f0&project=cbasdo&folder=&organizationId=)

Data Extraction - Python library bigquery was used to extract data from Google cloud. The steps to create Google API credentials can be figured out using this [webpage](https://console.cloud.google.com/apis/credentials). The following code snippet was run to fetch the data.

```python
pip install --upgrade google-cloud-bigquery        # install library
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r"C:\Users\Tauseef\Downloads\*******.json"   # replace the file name by your own google credentials
client = bigquery.Client()          # Start the BigQuery Client
QUERY = ('SELECT * FROM `bigquery-public-data.chicago_crime.crime`')              # Input Query Syntax
query_job = client.query(QUERY)     # Start Query API Request
query_result = query_job.result()   # Get Query Result
df = query_result.to_dataframe()    # Save the Query to Dataframe
```