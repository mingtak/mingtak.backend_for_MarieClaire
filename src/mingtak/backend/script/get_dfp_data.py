# -*- coding: utf-8 -*-
from googleads import dfp
import tempfile
from googleads import errors
import gzip
import csv
import io
from sqlalchemy import create_engine

DBSTR = 'mysql+mysqldb://MarieClaire:MarieClaire@localhost/MarieClaire?charset=utf8mb4'
ENGINE = create_engine(DBSTR, echo=True)


def execSql(execStr):
    conn = ENGINE.connect() # DB連線
    execResult = conn.execute(execStr)
    conn.close()
    if execResult.returns_rows:
        return execResult.fetchall()


def createExecStr(item, name):

    if name.lower() == 'line_item':
        execStr = \
            """INSERT INTO dfp_{}(
                   {}_ID, {}_NAME, ORDER_ID)
               VALUES ('{}', '{}', '{}')
               ON DUPLICATE KEY
               UPDATE {}_NAME = '{}'
            """.format(
                    name.lower(),
                    name.upper(),
                    name.upper(),
                    item.get('Dimension.%s_ID' % name.upper()),
                    item.get('Dimension.%s_NAME' % name.upper()).replace("'", "''"),
                    item.get('Dimension.ORDER_ID'),
                    name.upper(),
                    item.get('Dimension.%s_NAME' % name.upper()).replace("'", "''")
                )
        return execStr

    if name.lower() == 'order':
        execStr = \
            """INSERT INTO dfp_{}(
                   {}_ID, {}_NAME, ADVERTISER_ID)
               VALUES ('{}', '{}', '{}')
               ON DUPLICATE KEY
               UPDATE {}_NAME = '{}'
            """.format(
                    name.lower(),
                    name.upper(),
                    name.upper(),
                    item.get('Dimension.%s_ID' % name.upper()),
                    item.get('Dimension.%s_NAME' % name.upper()).replace("'", "''"),
                    item.get('Dimension.ADVERTISER_ID'),
                    name.upper(),
                    item.get('Dimension.%s_NAME' % name.upper()).replace("'", "''")
                )
        return execStr
    execStr = \
        """INSERT INTO dfp_{}(
               {}_ID, {}_NAME)
           VALUES ('{}', '{}')
           ON DUPLICATE KEY
           UPDATE {}_NAME = '{}'
        """.format(
                name.lower(),
                name.upper(),
                name.upper(),
                item.get('Dimension.%s_ID' % name.upper()),
                item.get('Dimension.%s_NAME' % name.upper()).replace("'", "''"),
                name.upper(),
                item.get('Dimension.%s_NAME' % name.upper()).replace("'", "''")
            )

    return execStr


def main(client):
    # Initialize a DataDownloader.
    report_downloader = client.GetDataDownloader(version='v201711')

    # Create report job.
    report_job = {
        'reportQuery': {
            'dimensions': ['LINE_ITEM_ID', 'LINE_ITEM_NAME', 'ORDER_ID', 'ORDER_NAME', 'DATE',
                           'ADVERTISER_NAME', 'ADVERTISER_ID'],
            'columns': ['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS', 'AD_SERVER_CTR'],
            'dateRangeType': 'REACH_LIFETIME' # 可能的值: 'TODAY', 'YESTERDAY', 'REACH_LIFETIME'
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
            resultList.append(item)
#    import pdb;pdb.set_trace()

    for item in resultList:
        # ADVERTISER
        execStr = createExecStr(item, 'ADVERTISER')
        execSql(execStr)
        # ORDER
        execStr = createExecStr(item, 'ORDER')
        execSql(execStr)
        # LINE ITEM
        execStr = createExecStr(item, 'LINE_ITEM')
        execSql(execStr)
        # AD SERVER
        execStr = \
           """SELECT id
              FROM dfp_ad_server
              WHERE ADVERTISER_ID = '{}' and LINE_ITEM_ID = '{}' and ORDER_ID = '{}' and DATE = '{}'
           """.format(
                    item.get('Dimension.ADVERTISER_ID'),
                    item.get('Dimension.LINE_ITEM_ID'),
                    item.get('Dimension.ORDER_ID'),
                    item.get('Dimension.DATE'),
               )
        resultId = execSql(execStr)
        if resultId:
            resultId = resultId[0][0]
        else:
            execStr = "select max(id) from dfp_ad_server"
            try:
                resultId = execSql(execStr)[0][0] + 1
            except:
                resultId = 1

#        import pdb; pdb.set_trace()
        execStr = \
            """INSERT INTO dfp_ad_server(id, ADVERTISER_ID, LINE_ITEM_ID, ORDER_ID, DATE, AD_SERVER_IMPRESSIONS, AD_SERVER_CLICKS, AD_SERVER_CTR)
               VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}', '{}')
               ON DUPLICATE KEY
               UPDATE AD_SERVER_IMPRESSIONS = '{}', AD_SERVER_CLICKS = '{}' , AD_SERVER_CTR = '{}'

            """.format(
                    resultId,
                    item.get('Dimension.ADVERTISER_ID'),
                    item.get('Dimension.LINE_ITEM_ID'),
                    item.get('Dimension.ORDER_ID'),
                    item.get('Dimension.DATE'),
                    item.get('Column.AD_SERVER_IMPRESSIONS'),
                    item.get('Column.AD_SERVER_CLICKS'),
                    item.get('Column.AD_SERVER_CTR'),
                    item.get('Column.AD_SERVER_IMPRESSIONS'),
                    item.get('Column.AD_SERVER_CLICKS'),
                    item.get('Column.AD_SERVER_CTR'),
                )
        execSql(execStr)

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

