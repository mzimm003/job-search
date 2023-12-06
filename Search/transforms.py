import json
from typing import (
    Dict,
    Tuple
)
from pathlib import Path

class Request:
    def __init__(
            self,
            method:str=None,
            url:str=None,
            headers:Dict[str,str]=None,
            data:str=None,
            ):
        self.method = 'GET' if method is None else method
        self.url = '' if url is None else url
        self.headers = {} if headers is None else headers
        self.data = '' if data is None else data

    def getOrg(self):
        orgName = self.url.lstrip('https://')
        orgName = orgName[:orgName.find('/')]
        return orgName

    def update(self, inp:str, searchPhrase:str, element='url'):
        {
            'url':self.__setURL,
            'headers':self.__updateHeaders,
            'method':self.__setMethod,
            'data':self.__setData,
        }[element](inp, searchPhrase)
    
    def __cleanInput(self, inp:str, searchPhrase:str):
        return (inp
                .replace("'","")
                .replace(Transform.PlainTextToHTML(searchPhrase),'____XsearchPhraseHTMLX____')
                .replace(Transform.HTMLTextToPlain(searchPhrase),'____XsearchPhrasePLAINX____'))

    def __setMethod(self, meth:str, searchPhrase:str):
        self.method = self.__cleanInput(meth, searchPhrase)
    
    def __setURL(self, url:str, searchPhrase:str):
        self.url = self.__cleanInput(url, searchPhrase)

    def __setData(self, data:str, searchPhrase:str):
        self.data = self.__cleanInput(data, searchPhrase)
    
    def __updateHeaders(self, par:str, searchPhrase:str):
        o, p = par.split(': ')
        o = self.__cleanInput(o, searchPhrase)
        p = self.__cleanInput(p, searchPhrase)
        # if o != 'Cookie':
        self.headers[o] = p
    
    def getRequestDict(self, searchPhrase):
        return json.loads(json.dumps(self.__dict__)
                          .replace("{","{{").replace("}","}}")
                          .replace("____X","{").replace("X____","}")
                          .format(searchPhraseHTML=Transform.PlainTextToHTML(searchPhrase),
                                  searchPhrasePLAIN=Transform.HTMLTextToPlain(searchPhrase)))

class Transform:
    def __init__(
            self,
            inFile:str | Path = 'Search/scratch.txt',
            outFile:str | Path = 'Search/searches.json',
            ) -> None:
        self.inFile:str | Path = inFile
        self.outFile:str | Path = outFile

    @staticmethod
    def HTMLTextToPlain(text:str):
        plain = (text
                 .replace('+',' ')
                 .replace('%20',' ')
                 )
        return plain
    
    @staticmethod
    def PlainTextToHTML(text:str):
        plain = (text
                 .replace(' ','+')
                 .replace(' ','%20')
                 )
        return plain

    def requestHeaderToRequestParamDict(
            self,
            ):
        dct = {}
        host = None
        with open(self.inFile, 'r') as f:
            contents = f.readlines()
            methodEndIdx = contents[0].find(' ')
            dct['method'] = contents[0][:methodEndIdx]
            dct['url'] = contents[0][methodEndIdx+1:contents[0].find(' ',methodEndIdx+1)]
            dct['headers'] = {}
            
            for l in contents[1:]:
                keyEndIdx = l.find(': ')
                key = l[:keyEndIdx]
                value = l[keyEndIdx+2:].replace('\n','')
                if key == 'Host':
                    dct['url'] = 'https://' + value + dct['url']
                    host = value
                else:
                    dct['headers'][key] = value
        
        contents = None
        with open(self.outFile, 'r') as f:
            contents = json.load(f)
            if 'Origin' in dct['headers']:
                contents[dct['headers']['Origin'].replace('https://','')] = dct
            else:
                contents[host] = dct

        with open(self.outFile, 'w') as f:
            json.dump(contents, f)

    def GUIRequestHeaderToRequest(
            self,
            input:str,
            searchPhrase:str,
            ):
        dct = {}
        host = None
        contents = input.split('\n')
        methodEndIdx = contents[0].find(' ')
        dct['method'] = contents[0][:methodEndIdx]
        dct['url'] = contents[0][methodEndIdx+1:contents[0].find(' ',methodEndIdx+1)].replace(searchPhrase,'{}')
        dct['headers'] = {}
        
        for l in contents[1:]:
            keyEndIdx = l.find(': ')
            key = l[:keyEndIdx]
            value = l[keyEndIdx+2:].replace('\n','')
            if key == 'Host':
                dct['url'] = 'https://' + value + dct['url']
                host = value
            else:
                dct['headers'][key] = value.replace(searchPhrase,'{}')
        
        return dct
    
    def GUICurlToRequest(
            self,
            input:str,
            searchPhrase:str,
            ):
        req = Request()
        curlMap = {
            '-X':'method',
            '--request':'method',
            '-H':'headers',
            '--header':'headers',
            '--data-raw':'data',
            '--data':'data',
            '-d':'data',
            '--compressed':None,
        }
        cursorIdx = 5
        nextCursorIdx = input.find(' ',cursorIdx)
        nextCursorIdx = len(input) if nextCursorIdx == -1 else nextCursorIdx
        req.update(input[cursorIdx:nextCursorIdx], searchPhrase)
        cursorIdx = nextCursorIdx

        while cursorIdx < len(input) and cursorIdx >= 0:
            nextCursorIdx = input.find(' ', cursorIdx+1)
            nextCursorIdx = len(input) if nextCursorIdx == -1 else nextCursorIdx
            option = input[cursorIdx:nextCursorIdx].lstrip(' ')
            if not option in curlMap:
                raise NotImplementedError('Curl option {} not yet implemented'.format(option))
            elif curlMap[option] is None:
                cursorIdx = nextCursorIdx
            else:                    
                cursorIdx = nextCursorIdx
                nextCursorIdx = input.find(' -', cursorIdx+1)
                nextCursorIdx = len(input) if nextCursorIdx == -1 else nextCursorIdx
                param = input[cursorIdx:nextCursorIdx].lstrip(' ')
                req.update(param, searchPhrase, curlMap[option])
                cursorIdx = nextCursorIdx
        return req

def main():
    Transform().requestHeaderToRequestParamDict()

if __name__ == "__main__":
    main()