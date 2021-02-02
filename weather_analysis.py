import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def lambda_handler(event, context):
    print("Make a connection to S3")
    s3 = boto3.client("s3")
    filename=''
    #Get the file name
    if event:
        file_obj = event["Records"][0]
        bucketname = str(file_obj['s3']['bucket']['name'])
        filename = str(file_obj['s3']['object']['key'])
    print("Filename: ", filename)
        
    #read the csv file with ObservationDate as a date
    filepath="s3://"+"zrpg-weather-data-analysis/"
    df=pd.read_csv(filepath+filename,delimiter=",",parse_dates=["ObservationDate"])

    #Remove unwanted columns for this analysis
    df1 = df[['ForecastSiteCode', 'ObservationDate','ScreenTemperature','SiteName','Latitude','Longitude','Region','Country']]
    
    #check if data frame is empty
    if df1.empty:
                        raise TypeError('Data frame has no data, check the source file')
    
    #temporarily replace Nan with empty string
    df2=df1.fillna('')
    
    #Get distinct of Region and country, this will be used to fill the missing values
    df_grouped = df2.groupby(['Region', 'Country']).size().reset_index(name='Freq')
    df_distinct_region_country= df_grouped[['Region','Country']]
    df_distinct_region_country=df_distinct_region_country[df_distinct_region_country.Country!='']
    
    #Fill the missing country values using the distinct region and country in df_distinct_region_country
    for index,row in df_distinct_region_country.iterrows():
        df2.loc[df2.Region == df_distinct_region_country['Region'][index], 'Country'] = df_distinct_region_country['Country'][index]
        
    #Convert data frame to a parquet file
    table = pa.Table.from_pandas(df2, preserve_index=False)
    pq.write_table(table, filepath+"parquet/"+filename.replace("csv", "parquet"))
    
    return 'Success'