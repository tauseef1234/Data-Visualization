<center><h1><font color = '#EC9C45'> Chicago crime data - Interactive Dashboard </font></h1></center>

The two interactive dashboards developed using open source visualization library **BOKEH** are aimed to derive key insights in criminal offences committed in the city of Chicago for the year 2019. The dashboard shows a choropleth map of the city of Chicago that has counties color coded by the offence count, a datatable and a horizontal bar chart of the offence types.




## Input Data

The source data for this dashboard is extracted from [Google cloud public dataset](https://console.cloud.google.com/marketplace/product/city-of-chicago-public-data/chicago-crime?filter=solution-type:dataset&id=a985ccaf-0a3a-4eb9-a2de-c4fd07de08f0&project=cbasdo&folder=&organizationId=)

Data Extraction - Python library bigquery was used to extract data from Google cloud. The steps to create Google API credentials can be figured out using Google authentication [webpage](https://cloud.google.com/docs/authentication/getting-started). The following code snippet was run to fetch the data.

```python
pip install --upgrade google-cloud-bigquery        # Install library
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r"C:\Users\*******.json"   # Replace the file name by your own google API credentials
client = bigquery.Client()          # Start the BigQuery Client
QUERY = ('SELECT * FROM `bigquery-public-data.chicago_crime.crime`')              # Input Query Syntax
query_job = client.query(QUERY)     # Start Query API Request
query_result = query_job.result()   # Get Query Result
df = query_result.to_dataframe()    # Save the Query to Dataframe
```
The pickle file `chicago_crime.pkl` is generated from the df dataframe using the above code snippet

**Google cloud stores data from 2001 till 2019 but this dashboard uses data for year 2019 only.**

The `Boundaries.geojson` (mapping data) json file is extracted from the [Chicago city website](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Neighborhoods/bbvz-uum9)

## Dashboard 1

[Dashboard1 Link](https://testchicago.herokuapp.com/)

This dashboard (chicago3.py) has three key components:

1. Choropleth map - A geomap in which county areas are color coded by the count of offence in the city of Chicago for the year 2019.
2. Datatable - A datatable view of the count by offence type
3. Bar chart - A horizontal bar chart is used to display the count by offence type

## How the dashboard works

When clicked on a county on the geomap, the datatable and horizontal bar chart get refreshed with the offence count by that county. When clicked on an offence type on datatable, the geomap gets resfreshed with the offence count by the offence type clicked on the data table. The dashboard is developed using Python interactive data visualization library __bokeh__.


## Dashboard 2

[Dashboard2 Link](https://chicago-offense.herokuapp.com/chicago_2019)

The second dashobard (chicago_2019.py) deep dives into the distribution of offences by month and offence type. The key components of this dashboard are:

1. Choropleth map - A geomap in which county areas are color coded by the count of offence in the city of Chicago for the year 2019.
2. Datatable - A datatable view of the percentage of offence by day of the week and time of the day
3. Bar chart - A horizontal bar chart is used to display the count by offence type and month


References:

1. [Bokeh documentation](https://docs.bokeh.org/en/latest/index.html) is the best place to get started with the library - great resource
2. This great [blog](https://jimking100.github.io/2019-09-04-Post-3/) from Jim King on creating an interactive geographic map using bokeh
