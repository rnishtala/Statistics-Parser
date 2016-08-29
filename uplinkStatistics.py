# @Author: rnishtala
# @Date:   2016-08-21T20:48:36-04:00
# @Last modified by:   rnishtala
# @Last modified time: 2016-08-27T17:45:40-04:00



import sys
import yaml
import re
from bs4 import BeautifulSoup
import urllib.request


def readURL():
    proxy_handler = urllib.request.ProxyHandler({'http':'66.82.3.130:80'})
    opener = urllib.request.build_opener(proxy_handler)
    urllib.request.install_opener(opener)
    response = urllib.request.urlopen('http://gue000000756.terminal.jupiter.hnops.net/cgi-bin/command.cgi?CommandStr=_COM_SYSMON_STATS?=1')
    content = response.read()
    print("Request Sent")
    contentString = content.decode("utf-8")
    return contentString

def writeResultsToFile():
    """
    Reads and html file from the same directory
    @param {None}
    @return {None}
    """
    response = readURL()
    with open('uplinkSummary.html', 'w') as outfile:
        outfile.write(response)
    outfile.close()

def readStreamData(idx):
    """
    Reading the Streams Acks and Nacks
    @param {none}
    @return {dictionary} (holds the Stream Acks and Nacks)
    """
    streamDict = dict()
    streamStats = []
    if idx == 2:
        stream = 'Stream(Overall)'
    else:
        stream = 'Stream(Last 15 minutes)'
    fname = 'uplinkSummary.html'
    fileHandle = open(fname)
    soup = BeautifulSoup(fileHandle, 'html.parser')
    table = soup.findAll('table')[idx].tbody.findAll('tr')
    for row in table:
        regex = re.compile('^St.*', re.IGNORECASE)
        #find entry matching Stream using regex
        burstType = row.find('td', text = regex)
        if burstType is None:
            continue
        burstTypeString = str(burstType.text)
        match = regex.search(burstTypeString)
        if match is not None:
            acks = str(row.findAll('td')[1].contents[0])
            nacks = str(row.findAll('td')[3].contents[0])
            streamStats.append({'Acks': acks,'Nacks': nacks})
            break
    streamDict[stream] = streamStats
    fileHandle.close()
    return streamDict

def readScmaData(idx):
    """
    Reads the Scma Acks and Nacks
    @param {none}
    @return {dictionary} (holds the Scma Data Acks and Nacks)
    """
    scmaDict = dict()
    scmaStats = []
    scma = ''
    if idx == 2:
        scma =  'Scma Data(Overall)'
    else:
        scma =  'Scma Data(Last 15 minutes)'
    fname = 'uplinkSummary.html'
    fileHandle = open(fname)
    soup = BeautifulSoup(fileHandle, 'html.parser')
    table = soup.findAll('table')[2].tbody.findAll('tr')
    for row in table:
        #find entry matching Scma Data using regex
        regex = re.compile('^Sc.*Data$', re.IGNORECASE)
        burstType = row.find('td', text = regex)
        if burstType is None:
            continue
        burstTypeString = str(burstType.text)
        match = regex.search(burstTypeString)
        if match is not None:
            acks = str(row.findAll('td')[1].contents[0])
            nacks = str(row.findAll('td')[3].contents[0])
            scmaStats.append({'Acks': acks,'Nacks': nacks})
            break
    scmaDict[scma] = scmaStats
    fileHandle.close()
    return scmaDict

def BWUsageStats():
    """
    Reads the PDUs sent and PDUs dropped
    @param {none}
    @return {dictionary} (holds the PDUs sent and PDUs dropped)
    """
    pduDict = dict()
    pduStats = []
    pduSent = 'Packets (PDU) Sent'
    pduDropped = 'Packets (PDU) Dropped'
    pduSentStats = ''
    pduDroppedStats = ''
    fname = 'uplinkSummary.html'
    fileHandle = open(fname)
    soup = BeautifulSoup(fileHandle, 'html.parser')
    table = soup.findAll('table')[1].tbody.findAll('tr')
    for row in table:
        statsType = row.findAll('td')[0].contents[0]
        if statsType == pduSent:
            pduSentStats = str(row.findAll('td')[1].contents[0])
        elif statsType == pduDropped:
            pduDroppedStats = str(row.findAll('td')[1].contents[0])
        if pduSentStats and pduDroppedStats:
            pduStats.append({'PDUs Sent': pduSentStats,'PDUs dropped': pduDroppedStats})
            break;
    pduDict['BW Usage'] = pduStats
    fileHandle.close()
    return pduDict


def main():
    """
    This is the main function
    """
    streamResults = dict()
    latestStreamResults = dict()
    scmaResults = dict()
    pduResults = dict()
    #writeResultsToFile()
    print("Received response")
    print("===========Statistics=============")
    streamResults = readStreamData(2)
    latestStreamResults = readStreamData(3)
    scmaResults = readScmaData(2)
    latestScmaResults = readScmaData(3)
    pduResults = BWUsageStats()
    statistics = dict(streamResults)
    statistics.update(scmaResults)
    statistics.update(pduResults)
    statistics.update(latestStreamResults)
    statistics.update(latestScmaResults)
    print(yaml.dump(statistics, default_flow_style=False))
    with open('statistics.yml', 'w') as outfile:
        outfile.write(yaml.dump(statistics, default_flow_style=False))
    print("statistics.yml generated")
    outfile.close()

if __name__ == "__main__":
    main()
