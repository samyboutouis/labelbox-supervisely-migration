import csv

def convert_name(labelbox_name):
    # Open CSV file with all the conversion labels
    with open('Labelbox to Supervisely Connections-Grid view.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        # In each row of the CSV file
        for row in reader:
            # Find the labelbox label and the corresponding supervisely one
            labelbox_title = row['Labelbox Title or Answer Text'][1:-1]
            supervisely_title = row['Supervisely Values'][1:-1]
            # If parameter is equal to the labelbox label, return the supervisely version
            if labelbox_name == labelbox_title:
                return supervisely_title
        # Else return original parameter
        return labelbox_name

if __name__ == "__main__":
    print(convert_name('architecture category'))