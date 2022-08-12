from collections import OrderedDict
from flask import Flask, jsonify, request
import os
import pandas as pd
from typing import List, Dict, Callable, Tuple
import datetime
import string

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


BASEURL = '/usr/local/projects/flask/dataCenter/oerv_obsdata'
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


def update(date_after: str = '2022-07-24') -> None:  # the short line is required
    '''
    Function: get lists of commit dates and commit ids
    '''
    os.system('git pull')
    os.system(
        'git log --pretty=format:"%cd,%H,%s" --date=format:"%Y-%m-%d" --after="{}" > ./commitlog.txt'.format(date_after))
    dates: List[str] = []
    commitID: List[str] = []
    with open('./commitlog.txt') as f:
        for line in f.readlines():
            temp = line[:-1].split(',')
            if temp[0] not in dates:
                dates.append(temp[0])
                commitID.append(temp[1])
    df = pd.DataFrame({'date': dates, 'id': commitID})
    df.to_csv('./date_id.csv', index=False)


@app.route('/getProjectStatistics')
def getProjectStatistics():
    os.system('git pull')
    with open('./obsData/projectStatistics.txt') as f:
        rawData = list(map(lambda line: line[:-1].split('  '), f.readlines()))
    return jsonify({'data': formatData(rawData)})


@app.route('/getDiff', methods=['GET', 'POST'])
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
    df.index = df.index.map(str)  # required: change dtype of index
    data = request.values
    print('this is data', data)
    if len(data):
        date1 = data.get('date1')
        date2 = data.get('date2')
        id1, id2 = df.loc[date1, 'id'], df.loc[date2, 'id']
    else:
        id1, id2 = df.iloc[3, 0], df.iloc[0, 0]

    return jsonify({'data': diff(id1, id2)})


if __name__ == '__main__':
    os.chdir(BASEURL)
    update()
    os.chdir(BASEURL + '/..')

    app.debug = True
    app.run('0.0.0.0', '8080')
