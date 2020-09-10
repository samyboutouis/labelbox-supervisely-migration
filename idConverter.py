import hashlib

# Function converts
def labelbox_to_supervisely(labelboxID, type, supervisely_set):
    hash_object = hashlib.blake2b()

    # Add the labelbox ID to the hashlib object and give it a unique hash code
    hash_object.update(labelboxID.encode('ascii'))

    # Convert the hashcode into a hex number and convert it to an int
    hex_number = hash_object.hexdigest()
    int_number = int(hex_number, 16)
    superviselyID = 0
    original_set_length = len(supervisely_set)

    if(type == "id"):
        # Reduce the hash code to 9 digits
        superviselyID = int_number % 10**9
        supervisely_set.add(superviselyID)
    elif(type == "classID"):
        # Reduce the hash code to 7 digits
        superviselyID = int_number % 10**7
        supervisely_set.add(superviselyID)
    else:
        # Reduce the hash code to 8 digits
        superviselyID = int_number % 10**8
        supervisely_set.add(superviselyID)

    # Checking errors if there are hash code collisions
    if(len(supervisely_set) != original_set_length):
        return superviselyID
    else:
        superviselyID += 1
        return superviselyID
    

if __name__ == "__main__":
    mySet = {}
    print(labelbox_to_supervisely("ck9d2nrjgrthy0742c8g6p9ha", "id", mySet))