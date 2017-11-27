# -*- coding: utf-8 -*- 
from googleads import dfp
import tempfile
from googleads import errors
import gzip
import csv
import io
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


DBSTR = 'mysql+mysqldb://MarieClaire:MarieClaire@localhost/MarieClaire?charset=utf8mb4'


def execSql(self, execStr):
    conn = ENGINE.connect() # DB連線
    execResult = conn.execute(execStr)
    conn.close()
    if execResult.returns_rows:
        return execResult.fetchall()


def main(client):
    # Initialize a DataDownloader.
    report_downloader = client.GetDataDownloader(version='v201711')

    # Create report job.
    report_job = {
        'reportQuery': {
            'dimensions': ['LINE_ITEM_ID', 'LINE_ITEM_NAME', 'ORDER_ID', 'ORDER_NAME', 'DATE',
                           'ADVERTISER_NAME', 'ADVERTISER_ID'],
            'columns': ['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS', 'AD_SERVER_CTR'],
            'dateRangeType': 'YESTERDAY'
        }
    }

    try:
        # Run the report and wait for it to finish.
        report_job_id = report_downloader.WaitForReport(report_job)
    except errors.DfpReportError, e:
        print 'Failed to generate report. Error was: %s' % e

    # Change to your preferred export format.
    export_format = 'CSV_DUMP'

    report_file = tempfile.NamedTemporaryFile(suffix='.csv.gz', delete=False)

    # Download report data.
    report_downloader.DownloadReportToFile(
        report_job_id, export_format, report_file)

    report_file.close()

    resultList = []
    with gzip.open('%s' % report_file.name, 'rb') as file:
        tmpDict = csv.DictReader(file)
        for item in tmpDict:
            print type(item)
            resultList.append(item)
#    import pdb;pdb.set_trace()

    # Display results.
    print 'Report job with id "%s" downloaded to:\n%s' % (
        report_job_id, report_file.name)


if __name__ == '__main__':
    # Initialize client object.
    dfp_client = dfp.DfpClient.LoadFromStorage()
    # Initialize a service.
    network_service = dfp_client.GetService('NetworkService', version='v201708')
    # Make a request.
    current_network = network_service.getCurrentNetwork()
    print 'Found network %s (%s)!' % (current_network['displayName'],
                                      current_network['networkCode'])

    main(dfp_client)

