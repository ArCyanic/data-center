from flask import Blueprint, jsonify, request
import os
import pandas as pd
from typing import List, Dict, Tuple, Callable
from Utils import Differ, match_ordered

appObservatoryProject = Blueprint('appObservatoryProject', __name__)


basePath = os.getcwd()
PROPERTIES = ['Project Name', 'Repo Name', 'Success Rate',
              'Total', 'Succeeded', 'Failed', 'Unresolvable']


def formatData(rawData):
    res = []
    data = [[row[0], row[1], round(float(row[3]) / (int(row[2]) if row[2] != '0' else 1), 2), int(
        row[2]), int(row[3]), int(row[4]), int(row[5])] for row in rawData]
    data.sort(key=lambda row: row[3], reverse=True)
    for i in range(len(data)):
        res.append({PROPERTIES[j]: data[i][j] for j in range(len(PROPERTIES))})
    return res


def getSummary(id: str) -> object:
    os.system('git checkout {} ./obsData/projectStatistics.txt'.format(id))

    with open('./obsData/projectStatistics.txt') as f:
        rawData = list(map(lambda line: line[:-1].split('  '), f.readlines()))

    classData = {line[0] + '  ' + line[1]: {'total': int(line[2]), 'success': int(line[3])} for line in rawData}

    summary = []
    classification = {'Core': ['openEuler:Mainline  standard'], 'Extend': [
        'openEuler:Epol  standard', 'openEuler:Factory  standard', 'Factory:RISC-V  22.09'], 'Third': []}

    for category in list(classification.keys()):
        temp = {'category': category, 'total': 0,
                'success': 0, 'successRate': 0.0}
        for project in classification[category]:
            temp['total'] += classData[project]['total']
            temp['success'] += classData[project]['success']
        temp['successRate'] = round(
            temp['success'] / temp['total'], 2) if temp['total'] else 0.0
        summary.append(temp)

    return summary


@appObservatoryProject.route('/getProjectStatistics')
def getProjectStatistics():
    with open('./oerv_obsdata/obsData/projectStatistics.txt') as f:
        rawData = list(map(lambda line: line[:-1].split('  '), f.readlines()))

    return jsonify({'data': formatData(rawData)})


@appObservatoryProject.route('/getTrend')
def getTrend():
    df = pd.read_csv('./oerv_obsdata/date_id.csv', index_col='date')
    dates = list(df.index)[::-1]
    res = []
    os.chdir(basePath + '/oerv_obsdata')
    for date in dates:
        temp = {'date': date, 'data': [], 'total': 0}
        temp['data'] = getSummary(df.loc[date, 'id'])
        for summary in temp['data']:
            temp['total'] += summary['total']
        res.append(temp)
    os.chdir(basePath)
    return jsonify({'data': res})


@appObservatoryProject.route('/getDiff', methods=['GET', 'POST'])
def getDiff():
    def compare(a: Dict, b: Dict):
        return a['Project Name'] == b['Project Name'] and a['Repo Name'] == b['Repo Name']

    # get commit id based on dates
    df = pd.read_csv('./oerv_obsdata/date_id.csv', index_col='date')
    data = request.values
    dates = list(df.index)
    date1 = dates[3]
    date2 = dates[0]
    id1, id2 = '', ''
    if len(data):
        date1 = data.get('date1')
        date2 = data.get('date2')
        id1, id2 = df.loc[date1, 'id'], df.loc[date2, 'id']
    else:
        id1, id2 = df.iloc[3, 0], df.iloc[0, 0]

    filePath = './obsData/projectStatistics.txt'
    repositoryPath = basePath + '/oerv_obsdata'
    def sortKey(line): return line['Total']
    differ = Differ(id1, id2, sortKey, formatData, True,
                    compare, filePath, repositoryPath, basePath)
    diffRes = differ.gitDiff()

    options = [{'label': date, 'value': date} for date in dates]
    return jsonify({'data': diffRes, 'date1': date1, 'date2': date2, 'options': options})
