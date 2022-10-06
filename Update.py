from flask import Blueprint, Response
import os
import pandas as pd
from typing import List


# import requests
# from requests.auth import HTTPBasicAuth
import re 

appUpdate = Blueprint('appUpdate', __name__)

BASEURL = os.getcwd()

@appUpdate.route('/updateLocal')
def updateLocal(date_after: str = '2022-07-26') -> None:  # the short line is required
    '''
    - Get lists of commit dates and commit ids
    - Generate a file that contains the names of all related projects
    '''
    os.chdir(BASEURL + '/oerv_obsdata')

    # Part I. Generate a csv file that contains information about dates and commit ids
    os.system('git pull origin master')
    os.system(
        'git log --pretty=format:"%cd,%H,%s" --date=format:"%Y-%m-%d" --after="{}" > ./commitlog.txt'.format(date_after))
    dates: List[str] = []
    commitID: List[str] = []
    with open('./commitlog.txt') as f:
        for line in f.readlines():
            temp = line[:-1].split(',')
            if temp[0] not in dates and temp[2][:2] == '20':
                dates.append(temp[0])
                commitID.append(temp[1])
    df = pd.DataFrame({'date': dates, 'id': commitID})
    df.to_csv('./date_id.csv', index=False)

    # Part II. Generate a txt file that contains information about the names of all related projects
    # with open('./obsData/projectStatistics.txt') as f1:
    #     with open('./projectsNames.txt', 'w') as f2:
    #         raw = f1.read()
    #         names = re.findall(r'^|\n(.*?)  (.*?)  ', raw)[1:]
    #         f2.write('\n'.join(['{},{}'.format(name[0], name[1]) for name in names]))

    os.chdir(BASEURL)
    return Response('Update Local Success')

@appUpdate.route('/updateRepository')
def updateRepository():
    # pull from remote
    os.chdir(BASEURL + '/oerv_script/oerv_obsdata')
    os.system('git pull --no-ff')

    os.chdir(BASEURL + '/oerv_script/script/')
    os.system('python main.py')
    os.chdir(BASEURL)   
    return Response('Update repository success')