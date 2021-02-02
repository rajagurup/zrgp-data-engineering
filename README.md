# zrgp-data-engineering
Data engineering

## Requirement-

Convert the weather data into parquet format. Set the raw group to appropriate value you see fit for this data.
The converted data should be queryable to answer the following question.
- Which date was the hottest day?
- What was the temperature on that day?
- In which region was the hottest day?

## High level design-

1. When a csv file is placed in s3 bucket, trigger an AWS lambda function
2. Use AWS lambda function with boto3 and pandas to clean and prepare the data.
3. Create a parquet file in s3 bucket. (This process will happen for every csv file through s3 bucket event)
4. Use AWS Glue crawler to create a table in AWS data catalogue for all parquet files under the given prefix.
5. Use Athena to Query the data catalogue table to view the desired data.
6. Generate a Tableau dashboard for non-technical users.

## Detailed design-

1. Python, Pandas is used for data cleaning and data preparation. 
2. Eye-balling the data shows that there the following operations needs to be done on the data set -
    a. Unused columns that can be removed - To make Athena queries cost less and to make the python job run faster. 
    b. Country Column has missing values. But, we can identify the country value by checking the country value present for the same region on other records. 
3. An s3 bucket is created in AWS with an event to create an AWS lambda function for all object create events.
4. An AWS lambda function with boto3, pandas and pyarrow is created to process every csv file and convert it into a parquet and data analysis.
    a. The lambda function will need a IAM role that has access to the S3 bucket and cloud watch (to create execution logs).
    b. Boto3 is available by default, but the libraries for Pandas, pyarrow for linux need to included in the deployment file. The size should not exceed 250MB.
5. For every csv file that is created, the AWS lambda function will now create a parquet file with the necessary data.
6. Create a glue crawler with the right settings to read all the parquet and create a single AWS data catalogue table.
    a. The glue crawler must have an IAM role with access to S3, Athena and Glue service.
    b. If lake formation is enabled in the account, grant permission for the data catalogue table to the Glue role (And the console role used for Athena) used by the crawler.
    c. Set a schedule for the glue crawler. The schedule of the Glue crawler is determined by the frequency with which the source file will be available.
7. Query the table through Athena to get the desired data.
8. There may be business users who may not wish to write queries. Create a Tableau Dashboard to present the desired data in a dashboard and publish it to a table server. 
9. Now the result of the data analysis is fully hands-free. It will work for any number of files. The user only needs to click the url of the dashboard to gain insight.
10. If the test result is a success, a terrform module can be created to automate the deployment process to the higher environments.

## Assumptions-

1. The provider of the file can place the file in AWS s3 bucket. If this is not the case, we can create an interface to do this.
2. The unused columns in the source data set is not expected to be used for any analysis. The Athena query executions is charged based of the volume of data read, so lesser the better.
