from flask import Blueprint, request, jsonify

import re 

import requests 

appMisc = Blueprint('appMisc', __name__)

@appMisc.route('/search-package', methods=['POST'])
def searchPackage():
    '''
    :return [(projectName, packageName), ...]
    '''
    def constructURL(target):
        base_url = 'https://build.tarsier-infra.com/search?'
        args = 'utf8=✓&search_text={}&search_for=0&name=1&attrib_type_id='.format(target)
        return base_url + args

    # get html text
    target = request.values[0]
    account = {'username': 'cyanic', 'password': '123456'}
    response = requests.get(constructURL(target), auth=requests.auth.HTTPBasicAuth(**account))
    text = response.text 

    # filter out all related path in form of [(projectName, packageName), ...]
    raw = re.findall(r'package .*?title="(.*?)".*?title="(.*?)"', text)
    with open('./oerv_obsdata/projectsNames.txt') as f:
        projectsNames = f.read().split('\n')
    res = list(filter(lambda name: name[0] in projectsNames, raw))
    return jsonify({'data': res})