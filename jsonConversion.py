from idConverter import labelbox_to_supervisely
import json

if __name__ == "__main__":

    # Load Book of Fortresses JSON file
    with open("export-2020-08-25T19_44_53.670Z.json") as f:
        data = json.load(f)
    labelbox_bof = data[0]

    # Initialize Supervisely version of Book of Fortresses
    supervisely_bof = {}
    supervisely_bof["description"] = ""
    supervisely_bof["tags"] = ""
    supervisely_bof["size"] = {}
    supervisely_bof["size"]["height"] = 10
    supervisely_bof["size"]["width"] = 10
    supervisely_bof["objects"] = []

    # Loop through each object
    object_list = labelbox_bof["Label"]["objects"]
    used_ids = set()

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
        new_object["lablerLogin"] = "edtriplett"
        
        # Creation time
        new_object["createdAt"] = "2020-06-02T17:02:42.352Z"
        new_object["updatedAt"] = "2020-06-14T23:20:32.100Z"

        # Make tags for the new object
        new_object["tags"] = []

        # If the labelbox object has classifications
        try: 
            classifications = object_list[i]["classifications"]
            for k in range(len(classifications)):
                new_object["tags"].append({})
                new_object["tags"][k]["id"] = labelbox_to_supervisely(classifications[k]["featureId"], "regular", used_ids)
        except:
            print("No classifications")
            
    