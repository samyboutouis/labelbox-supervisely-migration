
import json
import base64
import os


#Assuming cropped images to be converted to base64 are in 'cropped masks' folder, which is in the same directory as this script
directory = os.path.join(os.getcwd(), "cropped_masks")

img_dict = dict()
# Iterate through each folder of cropped images in cropped_masks
for filename in os.listdir(directory):
    folderdir = os.path.join(directory, filename)

    # Iterate through each cropped image in folder
    for imagefile in os.listdir(folderdir):

        # Get cropped image filepath
        imagedir = os.path.join(folderdir, imagefile)

        # Create dictionary entry where key = cropped image 'name' (featureId) and value = filepath to cropped image
        img_dict[imagefile[:len(imagefile)-4]] = imagedir

# Open, read, load Labelbox JSON
lfile = open("newjson/export-2020-08-25T19_44_53.670Z_instance_ID_fix_crop_origins_copy.json", encoding= 'utf-8', mode = 'r')

labelbox = json.load(lfile)

# Iterate through every image in JSON, and through every object in the image
for index, entry in enumerate(labelbox):
    for object_ind, obj in enumerate(entry['Label']['objects']):
        featureID = obj['featureId']

        # Get cropped image filepath corresponding to this featureId
        if featureID in img_dict.keys():
            imagepath = img_dict[featureID]

            # Create base64 encoding
            encoded = base64.b64encode(open(imagepath, "rb").read()).decode('utf-8')

            # Create 'bitmap' dictionary (Supervisely JSON has 'bitmap' dictionary with 'data' (base64 encoding) and
            # 'origin' as keys), save encoding in bitmap['data']
            labelbox[index]['Label']['objects'][object_ind]['bitmap'] = dict()
            labelbox[index]['Label']['objects'][object_ind]['bitmap']['data'] = encoded

            # to do later: origin is already in this JSON outside of the 'bitmap' dictionary, maybe move it inside
            # 'bitmap' later to match Supervisely format?

# Create folder and name for new JSON
newdirectory = os.path.join(os.getcwd(), "base64json")
output_file = "export-2020-08-25T19_44_53.670Z_instance_ID_fix_crop_origins_base64.json"

if not os.path.exists(newdirectory):
    os.mkdir(newdirectory)

# Save new JSON with base64 encodings
with open(os.path.join(newdirectory, output_file), 'w', encoding='utf-8') as f:
    json.dump(labelbox, f, ensure_ascii=False, indent=4)

