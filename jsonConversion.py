from idConverter import labelbox_to_supervisely
from nameConverter import convert_name
import json
import csv

if __name__ == "__main__":

    # Load Book of Fortresses JSON file
    with open("export-2020-08-25T19_44_53.670Z.json") as f:
        data = json.load(f)
    labelbox_bof = data[0]

    # Initialize Supervisely version of Book of Fortresses
    supervisely_bof = {}
    supervisely_bof["description"] = ""
    supervisely_bof["tags"] = []
    supervisely_bof["size"] = {}
    supervisely_bof["size"]["height"] = 10
    supervisely_bof["size"]["width"] = 10
    supervisely_bof["objects"] = []

    # Loop through each object
    object_list = labelbox_bof["Label"]["objects"]
    used_ids = set()

    reader = ""
    # Open CSV file with all the conversion labels
    with open('Labelbox to Supervisely Connections-Grid view.csv') as csvfile:
        reader = csv.DictReader(csvfile)

    for i in range(len(object_list)):
        # Create a new object
        new_object = {}

        # Collect the labelbox ID and convert it into a supervisely ID and save it in the new object
        object_id = labelbox_to_supervisely(object_list[i]["featureId"], "id", used_ids)
        new_object["id"] = object_id

        # Collect the labelbox ID and convert it into a supervisely class ID
        class_id = labelbox_to_supervisely(object_list[i]["featureId"], "classID", used_ids)
        new_object["classId"] = class_id

        # Set description to null
        new_object["description"] = ""

        # types of polygon, bitmap, line, point
        new_object["geometryType"] = "bitmap"
        new_object["labelerLogin"] = "edtriplett"

        # Creation time
        new_object["createdAt"] = "2020-06-02T17:02:42.352Z"
        new_object["updatedAt"] = "2020-06-14T23:20:32.100Z"

        # Make tags for the new object
        new_object["tags"] = []
        class_title = ""

        # If the labelbox object has classifications
        try: 
            # Set classifications to classifications sub-hierarchy
            classifications = object_list[i]["classifications"]

            # For each classification, append to tags a JSON object 
            for k in range(len(classifications)):
                new_object["tags"].append({})

                # Get and set ID of feature
                new_object["tags"][k]["id"] = labelbox_to_supervisely(classifications[k]["featureId"], "regular", used_ids)

                # Set name or question of the tag
                new_object["tags"][k]["name"] = convert_name(classifications[k]["title"])

                if type(classifications[k]["answer"]) is dict:
                    # Set value of the tag
                    new_object["tags"][k]["value"] = convert_name(classifications[k]["answer"]["title"])
                    if(k == 0):
                        class_title = new_object["tags"][k]["value"]
                else:
                    # Set value of the tag
                    new_object["tags"][k]["value"] = convert_name(classifications[k]["answer"])

                # Set extraneous tags
                new_object["tags"][k]["lablerLogin"] = "edtriplett"
                new_object["tags"][k]["createdAt"] = "2020-06-02T17:02:42.352Z"
                new_object["tags"][k]["updatedAt"] = "2020-06-14T23:20:32.100Z"
        except:
            print("No classifications")
        
        new_object["classTitle"] = class_title
        new_object["bitmap"] = {}

        # Base64 encoding goes here
        new_object["bitmap"]["data"] = ""

        # Origin goes here
        new_object["bitmap"]["origin"] = []

        supervisely_bof["objects"].append(new_object)

    with open('test.json', 'w') as outfile:
        json.dump(supervisely_bof, outfile, indent=4)
            
    