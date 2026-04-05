import json

def readFile(FileName: str):
    with open(FileName,'r') as file:
        fileData = json.load(file)

    return fileData
        
