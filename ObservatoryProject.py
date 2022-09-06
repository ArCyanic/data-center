from flask import Blueprint, jsonify, request
import os
import pandas as pd
from typing import List, Dict, Callable, Tuple

appObservatoryProject = Blueprint('appObservatoryProject', __name__)


BASEURL = os.getcwd() + '/oerv_obsdata'
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
    classification = {'Core': ['openEuler:Mainline  standard'], 'Extend': ['openEuler:Epol  standard', 'openEuler:Factory  standard', 'Factory:RISC-V  22.09'], 'Third': []}
    
    for category in list(classification.keys()):
        temp = {'category': category, 'total': 0, 'success': 0, 'successRate': 0.0}
        for project in classification[category]:
            temp['total'] += classData[project]['total']
            temp['success'] += classData[project]['success']
        temp['successRate'] = round(temp['success'] / temp['total'], 2) if temp['total'] else 0.0
        summary.append(temp)
            
    return summary

@appObservatoryProject.route('/getProjectStatistics')
def getProjectStatistics():    
    with open('./oerv_obsdata/obsData/projectStatistics.txt') as f:
        rawData = list(map(lambda line: line[:-1].split('  '), f.readlines()))
    
    return jsonify({'data': formatData(rawData)})

@appObservatoryProject.route('/getTrend')
def getTrend():
    os.chdir(BASEURL)
    df = pd.read_csv('./date_id.csv', index_col='date')
    dates = list(df.index)[::-1]
    res = []
    for date in dates:
        temp = {'date': date, 'data': [], 'total': 0}
        temp['data'] = getSummary(df.loc[date, 'id'])
        for summary in temp['data']:
            temp['total'] += summary['total']
        res.append(temp)
    os.chdir(BASEURL + '/..')
    return jsonify({'data': res})

@appObservatoryProject.route('/getDiff', methods=['GET', 'POST'])
def getDiff():
    def compare(a: Dict, b: Dict):
        return a['Project Name'] == b['Project Name'] and a['Repo Name'] == b['Repo Name']

    def match(seq1: List, seq2: List, compare: Callable) -> Tuple[List, List, List, List]:
        '''
        given two sequence, find the matching items and remaining elements based on compare function
        this is a string match problem
        return (seq1, seq2, former, latter)
        Another traverse method: arr[:], see https://www.cnblogs.com/HZL2017/p/8894215.html
        '''
        matched1, matched2 = [], []
        mark = len(seq2) - 1
        for i in range(len(seq1) - 1, -1, -1):
            for j in range(mark, -1, -1):
                if compare(seq1[i], seq2[j]):
                    matched1.append(seq1.pop(i))
                    matched2.append(seq2.pop(j))
                    mark = j - 1
                    break
        return (seq1, seq2, matched1, matched2)

    def diff(id1: str, id2: str) -> Dict:
        os.system(
            'git diff {} {} ./obsData/projectStatistics.txt > {}'.format(id1, id2, './diff.txt'))
        # read data to variables deleted and added
        deleted: List = []
        added: List = []
        with open('./diff.txt') as f:
            lines = f.readlines()
            # start from 6th line
            for i in range(6, len(lines)):
                if lines[i][0] == '-':
                    # strip off + / - and new line character
                    deleted.append(lines[i][1:-1].split('  '))
                elif lines[i][0] == '+':
                    added.append(lines[i][1:-1].split('  '))
        added = formatData(added)
        deleted = formatData(deleted)

        # construct diff
        matched: Tuple[List, List, List, List] = match(deleted, added, compare)
        diff: Dict[str, List] = {'former': matched[2], 'latter': matched[3], 'add': matched[0],
                                 'delete': matched[1]}

        # item['addition'] means type when data type is 'add' for 'delete', otherwise means index in their own type sequence
        formerCount, latterCount = -1, 1
        res = []
        for key, values in diff.items():
            for value in values:
                if key == 'former':
                    value['addition'] = formerCount
                    formerCount -= 1
                elif key == 'latter':
                    value['addition'] = latterCount
                    latterCount += 1
                else:
                    value['addition'] = key
                res.append(value)
        return sorted(res, key= lambda line: line['Total'], reverse=True)

    os.chdir(BASEURL)
    df = pd.read_csv('./date_id.csv', index_col='date')
    
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

    options = [{'label': date, 'value': date} for date in dates]
    diffRes = diff(id1, id2)
    os.chdir(BASEURL + '/..')
    return jsonify({'data': diffRes, 'date1': date1, 'date2': date2, 'options': options})
