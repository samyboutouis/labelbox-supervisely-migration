import csv

def convert_name(labelbox_name):
    with open('names.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            labelbox_title = row['Labelbox Title or Answer Text'].strip()
            supervisely_title = row['Supervisely Values'].strip()
            if labelbox_name == labelbox_title:
                return supervisely_title
        return labelbox_name

if n
