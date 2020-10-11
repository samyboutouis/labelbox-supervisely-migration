import json
import os
import pandas

from idConverter import labelbox_to_supervisely

# Get dataframe of Labelbox to Supervisely connections
lbox_sv = pandas.read_csv("New_Labelbox_to_Supervisely_Connections.csv")

# Dictionaries to hold mapping
answers_to_values = {}
answers_to_names = {}
titles_to_names = {}
answers_to_classTitles = {}
objtitles_to_classTitles = {}

# No Supervisely equivalent (label is in csv, but Supervisely column is blank)
no_sv = []

# Create mappings --------------------------------------------------------------------------------

for i in range(len(lbox_sv["Labelbox category"])):

    # Supervisely Category entry is blank; no Supervisely equivalent
    if not isinstance(lbox_sv["Supervisely Category"][i], str):
        no_sv.append(lbox_sv["Labelbox Title or Answer Text"][i].strip('"'))

    # This is a Labelbox "answer" to Supervisely "value" pair
    elif "answer" in lbox_sv["Labelbox category"][i] and "value" in lbox_sv["Supervisely Category"][i]:

        # Record mapping
        answers_to_values[lbox_sv["Labelbox Title or Answer Text"][i].strip('"')] = lbox_sv["Supervisely Values"][i].strip('"')

    # This is a Labelbox "answer" to Supervisely "name" pair
    elif "answer" in lbox_sv["Labelbox category"][i] and "name" in lbox_sv["Supervisely Category"][i]:

        # Record mapping
        answers_to_names[lbox_sv["Labelbox Title or Answer Text"][i].strip('"')] = lbox_sv["Supervisely Values"][i].strip('"')

    # This is a Labelbox "title" to Supervisely "name" pair
    elif "answer" not in lbox_sv["Labelbox category"][i] and "name" in lbox_sv["Supervisely Category"][i]:

        # Record mapping
        titles_to_names[lbox_sv["Labelbox Title or Answer Text"][i].strip('"')] = lbox_sv["Supervisely Values"][i].strip('"')

    # This is a Labelbox "answer" to Supervisely "classTitle" pair (should be fairly few, only for some fortification elements?)
    elif "answer" in lbox_sv["Labelbox category"][i] and "classTitle" in lbox_sv["Supervisely Category"][i]:

        # Record mapping
        answers_to_classTitles[lbox_sv["Labelbox Title or Answer Text"][i].strip('"')] = lbox_sv["Supervisely Values"][i].strip('"')

    # This is a Labelbox "title" (NOT under "classifications") to Supervisely "classTitle" pair
    else:
        objtitles_to_classTitles[lbox_sv["Labelbox Title or Answer Text"][i].strip('"')] = lbox_sv["Supervisely Values"][i].strip('"')


# Parse Labelbox JSON -------------------------------------------------------------------------------------

# Open JSON
lfile = open("base64json/base64-export-2020-08-25T19_44_53.670Z_instance_ID_fix_crop_origins.json", encoding='utf-8', mode='r')
labelbox = json.load(lfile)


# Record titles and answers not found
titlesnothere = []
answersnothere = []

# No Supervisely equivalent (label is in csv, but the Supervisely column is blank)
notinsv = 0

# Objects with no classifications field
noclass = []

for index, entry in enumerate(labelbox):
    # Initialize Supervisely version of JSON object with miscellaneous fields
    supervisely_bof = {}
    supervisely_bof["description"] = ""
    supervisely_bof["tags"] = ""
    supervisely_bof["size"] = {}
    supervisely_bof["size"]["height"] = 10  # Arbitrary value
    supervisely_bof["size"]["width"] = 10  # Arbitrary value
    supervisely_bof["objects"] = []
    used_ids = set()
    for object_ind, obj in enumerate(entry['Label']['objects']):
        s_obj = {}
        object_id = labelbox_to_supervisely(obj["featureId"], "id", used_ids)
        s_obj["id"] = object_id
        class_id = labelbox_to_supervisely(obj["featureId"], "classID", used_ids)
        s_obj["classId"] = class_id
        s_obj["description"] = ""
        s_obj["geometryType"] = "bitmap"
        s_obj["lablerLogin"] = "edtriplett"
        # Creation time
        s_obj["createdAt"] = "2020-06-02T17:02:42.352Z"
        s_obj["updatedAt"] = "2020-06-14T23:20:32.100Z"
        s_obj["tags"] = []

        # Class title
        if obj["title"] in objtitles_to_classTitles:
            s_obj["classTitle"] = objtitles_to_classTitles[obj["title"]]
        elif obj['title'] == "latitude and longitude of known points":
            s_obj["classTitle"] = objtitles_to_classTitles["Latitude and Longitude of known points"]
        else:
            # May change later on below for a few fortification elements, but generally should be obj["title"]
            s_obj["classTitle"] = obj["title"]

        if ("classifications" not in obj):
            noclass.append(obj['title'])
            s_obj["tags"].append("THERE ARE NO CLASSIFICATIONS FOR THIS OBJECT.")

        if ("classifications" in obj):

            # Initialize values
            classifications = obj["classifications"]
            for k in range(len(classifications)):
                s_obj["tags"].append({})
                s_obj["tags"][k]["name"] = ""
                s_obj["tags"][k]["value"] = ""

                # Create ID
                s_obj["tags"][k]["id"] = labelbox_to_supervisely(classifications[k]["featureId"], "regular", used_ids)

                # Parse title -----------------------------------------------------------------------------
                # Titles to names
                if classifications[k]["title"] in titles_to_names:
                    s_obj["tags"][k]["name"] = titles_to_names[classifications[k]["title"]]

                # No Supervisely equivalent (notinsv+=1 is just a placeholder instruction, not used for anything)
                elif classifications[k]["title"] in no_sv:
                    notinsv += 1

                # Check some spelling/capitalization errors
                elif classifications[k]["title"] == "Facade shape":
                    s_obj["tags"][k]["name"] = titles_to_names["Facade Shape"]

                elif classifications[k]["title"] == "Front facade, side facade or roof?":
                    s_obj["tags"][k]["name"] = titles_to_names["Front Facade, Side, Roof?"]

                elif classifications[k]["title"] == "Keep shape":
                    s_obj["tags"][k]["name"] = titles_to_names["Keep Shape"]

                elif classifications[k]["title"] == "Under sail?":
                    s_obj["tags"][k]["name"] = titles_to_names["Under Sail?"]


                # Title isn't found anywhere
                else:
                    titlesnothere.append(classifications[k]["title"])

                # Parse answer ---------------------------------------------------------------------------
                # If no answer field:
                if "answer" in classifications[k]:

                    # If answer field is a String:
                    if isinstance(classifications[k]["answer"], str):

                        # Scale bar -- answer is the String answer field
                        if obj['title'] == "scale bar":
                            s_obj["tags"][k]["value"] = classifications[k]["answer"]

                        # Location object -- answer is the String answer field
                        # This label actually is in the csv, but since the answer is a number that varies,
                        # we are checking it manually here
                        elif obj['title'] == "latitude and longitude of known points":
                            s_obj["tags"][k]["value"] = classifications[k]["answer"]

                        # This label actually is in the csv, but since the answer is a number that varies,
                        # we are checking it manually here
                        elif classifications[k]['title'] == "Number of merlons (numbers only)" or classifications[k]['title'] == "Number of merlons (number only)":
                            s_obj["tags"][k]["value"] = classifications[k]["answer"]

                        # This label actually is in the csv, but since the answer is a number that varies,
                        # we are checking it manually here
                        elif classifications[k]['title'] == "(Roughly) How many trees in the set? (numbers only)":
                            s_obj["tags"][k]["value"] = classifications[k]["answer"]

                        else:
                            print(classifications[k]['title'] + " " + classifications[k]["answer"] + " non-dictionary answer field not considered")


                    # Found in answers to names
                    elif classifications[k]["answer"]["title"] in answers_to_names:
                        s_obj["tags"][k]["name"] = answers_to_names[classifications[k]["answer"]["title"]]

                    # Found in answers to values
                    elif classifications[k]["answer"]["title"] in answers_to_values:
                        s_obj["tags"][k]["value"] = answers_to_values[classifications[k]["answer"]["title"]]

                    # Labelbox answer maps to object classTitle, should just be for a few fortification elements
                    elif classifications[k]["answer"]['title'] in answers_to_classTitles:
                        s_obj["classTitle"] = answers_to_classTitles[classifications[k]["answer"]['title']]

                    # No Supervisely equivalent (notinsv+=1 is just a placeholder instruction, not used for anything)
                    elif classifications[k]["answer"]["title"] in no_sv:
                        notinsv += 1

                    # Check for some spelling/capitalization errors
                    elif classifications[k]["answer"]["title"] == 'Hung "Criminal"':
                        s_obj["tags"][k]["value"] = answers_to_values['Hung "Criminal']

                    elif classifications[k]["answer"]["title"] == 'side Facade':
                        s_obj["tags"][k]["value"] = answers_to_values['Side Facade']

                    elif classifications[k]["answer"]["title"] == 'Front suface':
                        s_obj["tags"][k]["value"] = answers_to_values['Front surface']

                    elif classifications[k]["answer"]["title"] == 'Cyprus (Shaply pointed)':
                        s_obj["tags"][k]["value"] = answers_to_values['Cyprus (Sharply pointed)']

                    # Answer not found, need to check
                    else:
                        answersnothere.append(classifications[k]["answer"]["title"])


                # Deal with still-empty name or value fields --------------------------------------------------------------------

                # If name or value is still blank and title/answer are in 'not found' lists, say we are pending resolution
                if ("answer" in classifications[k]) and (isinstance(classifications[k]['answer'], dict)) and ((classifications[k]["answer"]["title"] in answersnothere) or (classifications[k]["title"] in titlesnothere)):
                    if s_obj["tags"][k]["name"] == "":
                        s_obj["tags"][k]["name"] = "NOT FOUND, PENDING RESOLUTION FOR THIS VALUE WITH TITLE " + classifications[k]["title"]

                    if s_obj["tags"][k]["value"] == "":
                        s_obj["tags"][k]["value"] = "NOT FOUND, PENDING RESOLUTION FOR THIS VALUE WITH TITLE " + classifications[k]["title"]

                # If name or value is still blank and title/answer are not in 'not found' lists, no Supervisely equivalent
                if s_obj["tags"][k]["name"] == "":
                    s_obj["tags"][k]["name"] = "NO SUPERVISELY EQUIVALENT for title " + classifications[k]["title"]

                if s_obj["tags"][k]["value"] == "":
                    s_obj["tags"][k]["value"] = "NO SUPERVISELY EQUIVALENT for title " + classifications[k]["title"]

                s_obj["tags"][k]["lablerLogin"] = "edtriplett"
                s_obj["tags"][k]["createdAt"] = "2020-06-02T17:02:42.352Z"
                s_obj["tags"][k]["updatedAt"] = "2020-06-14T23:20:32.100Z"

        s_obj["bitmap"] = {}

        # Base64 encoding goes here
        if "bitmap" in obj:
            s_obj["bitmap"]["data"] = obj['bitmap']['data']

        # Origin goes here
        if "origin" in obj:
            s_obj["bitmap"]["origin"] = obj['origin']

        supervisely_bof["objects"].append(s_obj)

    newdirectory = os.path.join(os.getcwd(), "supervisely_jsons")

    # Set file name for JSON, should be the image name (e.g. moura2.jpg, elvas1.jpg, etc.)
    output_file = entry["External ID"] + ".json"

    if not os.path.exists(newdirectory):
        os.mkdir(newdirectory)
    with open(os.path.join(newdirectory, output_file), 'w', encoding='utf-8') as f:
        json.dump(supervisely_bof, f, ensure_ascii=False, indent=4)

# For reference, printing what needs to be resolved
# print(set(titlesnothere))
# print(set(answersnothere))
# print(len(noclass))
# print(set(noclass))