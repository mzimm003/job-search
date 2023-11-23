import json
from pathlib import Path

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
                 .replace('+',' '))
        return plain
    
    @staticmethod
    def PlainTextToHTML(text:str):
        plain = (text
                 .replace(' ','+'))
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

    def GUIRequestHeaderToRequestParamDict(
            self,
            input,
            ):
        dct = {}
        host = None
        contents = input.split('\n')
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
        
        return dct
            

def main():
    Transform().requestHeaderToRequestParamDict()

if __name__ == "__main__":
    main()