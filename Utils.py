from typing import Callable, List, Tuple, Dict
import os


def match_ordered(seq1: List, seq2: List, compare: Callable) -> Dict[str, List]:
    '''
    Given two ordered sequence, find the matching items and remaining elements based on compare function
    Just using two loop.
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
    return {'unique1': seq1, 'unique2': seq2, 'matched1': matched1, 'matched2': matched2}


def match_unordered(seq1: List, seq2: List, compareKeys: str) -> Dict[str, List]:
    '''
    Given two unordered sequences, segment them into unique and matching segmentation based on compareKeys
    Here I combine the values which correspond to the compareKeys and hash them.
    Based on hash value, using set methods to fastly segment data.
    '''
    # construct hash map
    hash1 = {hash(''.join([str(item[compareKey])
                  for compareKey in compareKeys])): item for item in seq1}
    hash2 = {hash(''.join([str(item[compareKey])
                  for compareKey in compareKeys])): item for item in seq2}

    # get hash value intersection
    hashValues1 = set(hash1.keys())
    hashValues2 = set(hash2.keys())
    intersection = hashValues1.intersection(hashValues2)

    # segment data based on intersection and difference of hash value
    unique1 = [hash1[hashValue]
               for hashValue in hashValues1.difference(hashValues2)]
    unique2 = [hash2[hashValue]
               for hashValue in hashValues2.difference(hashValues1)]
    matched1, matched2 = [], []
    for hashValue in intersection:
        matched1.append(hash1[hashValue])
        matched2.append(hash2[hashValue])
    return {'unique1': unique1, 'unique2': unique2, 'matched1': matched1, 'matched2': matched2}


class Differ:
    def __init__(self, id1: str, id2: str, sortKey: Callable, formatter: Callable, ordered: bool, comparer, filePath: str, repositoryPath: str, basePath: str):
        '''
        When ordered is True, comparer is Callable type
        When ordered is False, comparer is List[str] type 
        '''
        self.id1 = id1
        self.id2 = id2
        self.sortKey = sortKey
        self.formatter = formatter
        self.comparer = comparer
        self.ordered = ordered
        self.filePath = filePath
        self.repositoryPath = repositoryPath
        self.basePath = basePath

    def gitDiff(self):
        os.chdir(self.repositoryPath)
        os.system(
            'git diff {} {} {} > {}'.format(self.id1, self.id2, self.filePath, './diff.txt'))
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
        os.chdir(self.basePath)
        added = self.formatter(added)
        deleted = self.formatter(deleted)

        # construct diff
        matchRes = match_ordered(deleted, added, self.comparer) if self.ordered else match_unordered(
            deleted, added, self.comparer)
        print(matchRes)
        diff: Dict[str, List] = {'former': matchRes['matched1'], 'latter': matchRes['matched2'], 'add': matchRes['unique2'],
                                 'delete': matchRes['unique1']}

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
        return sorted(res, key=self.sortKey, reverse=True)
