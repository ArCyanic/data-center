from struct import pack
from flask import Blueprint, request, jsonify
from typing import Dict, List
import os
import re
import pandas as pd
import requests

from Utils import Differ

appObservatoryPackages = Blueprint('appObservatoryPackages', __name__)


@appObservatoryPackages.route('/search-package', methods=['POST'])
def searchPackage():
    '''
    :return [(projectName, packageName), ...]
    '''
    def constructURL(target):
        base_url = 'https://build.tarsier-infra.com/search?'
        args = 'utf8=✓&search_text={}&search_for=0&name=1&attrib_type_id='.format(
            target)
        return base_url + args

    # get html text
    target = request.values.get('packageName', 'gcc')
    account = {'username': 'cyanic', 'password': '123456'}
    response = requests.get(constructURL(
        target), auth=requests.auth.HTTPBasicAuth(**account))
    text = response.text

    # filter out all related path in form of [(projectName, packageName), ...]
    raw = re.findall(r'package .*?title="(.*?)".*?title="(.*?)"', text)

    with open('./oerv_obsdata/obsData/projectStatistics.txt') as f1:
        projectsNames = set(re.findall(r'^|\n(.*?)  ', f1.read())[1:])
        print(projectsNames)

    res = list(filter(lambda name: name[0] in projectsNames, raw))
    res = [{'projectName': item[0], 'packageName': item[1]} for item in res]
    print('res', res)
    return jsonify({'data': res})


@appObservatoryPackages.route('/getRepositories')
def getRepositories():
    with open('./oerv_obsdata/obsData/projectStatistics.txt') as f:
        namePairs = re.findall(r'^|\n(.*?)  (.*?)  ', f.read())[1:]
    res = {}
    for pair in namePairs:
        if pair[0] not in res:
            res[pair[0]] = [pair[1]]
        else:
            res[pair[0]].append(pair[1])
    res = [{'value': key, 'label': key, 'children': [{'value': v, 'label': v}
                                                     for v in val]} for key, val in res.items()]
    return jsonify({'data': res})


@appObservatoryPackages.route('/getPackagesDiffSpatial', methods=['POST'])
def getPackagesDiffSpatial():

    def diff(path1, path2) -> Dict[str, List[Dict[str, str]]]:
        def extract(path) -> Dict[str, str]:
            f = open(path)
            data = {pair[0]: pair[1] for pair in list(
                map(lambda s: s.split('  '), f.read().split('\n')))[:-1]}
            f.close()
            return data

        data1 = extract(path1)
        data2 = extract(path2)

        packageNames1 = set(data1.keys())
        packageNames2 = set(data2.keys())
        intersection = packageNames1.intersection(packageNames2)
        unique1 = [{'packageName': packageName, 'status': data1[packageName]}
                   for packageName in packageNames1.difference(packageNames2)]
        unique2 = [{'packageName': packageName, 'status': data2[packageName]}
                   for packageName in packageNames2.difference(packageNames1)]

        same = []
        diff = []
        for packageName in intersection:
            status1, status2 = data1[packageName], data2[packageName]
            if status1 == status2:
                same.append({'packageName': packageName, 'status': status1})
            else:
                diff.append({'packageName': packageName,
                            'status1': status1, 'status2': status2})
        return {'unique1': unique1, 'unique2': unique2, 'same': same, 'diff': diff}

    # repositoryName1, repositoryName2 = request.values.values
    repositoryName1, repositoryName2 = request.values.get(
        'repositoryName1'), request.values.get('repositoryName2')
    path1 = './oerv_obsdata/obsData/' + \
        repositoryName1.replace(':', '+') + '.list'
    path2 = './oerv_obsdata/obsData/' + \
        repositoryName2.replace(':', '+') + '.list'
    res = diff(path1, path2)
    return jsonify(res)


@appObservatoryPackages.route('/getDates', methods=['POST'])
def getDates():
    path = './oerv_obsdata/timeline/' + \
        request.values.get('repositoryName').replace(':', '+') + '.txt'
    dates = []
    with open(path) as f:
        for line in f.readlines():
            date = line[:10]
            if date not in dates:
                dates.append(date)
    dates.reverse()
    return jsonify({'dates': dates})


@appObservatoryPackages.route('/getPackagesDiffTemporal', methods=['POST'])
def getPackagesDiffTemporal():
    basePath = os.getcwd()
    repositoryPath = basePath + '/oerv_obsdata'
    filePath = './obsData/' + \
        request.values.get('repositoryName').replace(':', '+') + '.list'

    # get ids
    df = pd.read_csv('./oerv_obsdata/date_id.csv', index_col='date')
    data = request.values
    date1 = data.get('date1')
    date2 = data.get('date2')
    # print(date1 in list(df.index))
    id1, id2 = df.loc[date1, 'id'], df.loc[date2, 'id']

    def sortKey(item): return item['Package Name']

    def formatter(data): return [
        {'Package Name': item[0], 'Status': item[1]} for item in data]
    compare = ['Package Name']
    differ = Differ(id1, id2, sortKey, formatter, False,
                    compare, filePath, repositoryPath, basePath)
    diffRes = differ.gitDiff()

    return jsonify({'data': diffRes})
