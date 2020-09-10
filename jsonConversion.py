from idConverter import labelbox_to_supervisely
import json

if __name__ == "__main__":
    with open("export-2020-08-25T19_44_53.670Z.json") as f:
        data = json.load(f)
    
    print(data[])