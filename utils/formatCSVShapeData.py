import csv

def formatCSVShapeData(path, user_class):
    with open(path, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)

    # Get the headers
    headers = data[0]

    # Get the data
    data = data[1:]

    # Create a list of dictionaries
    formatted_data = []
    for row in data:
        edited_data = {}
        for i in range(len(headers)):
            edited_data[headers[i]] = row[i]
        edited_data['users'] = int(edited_data['users'])
        edited_data['duration'] = int(edited_data['duration'])
        edited_data['spawn_rate'] = 1000
        edited_data['user_classes'] = [user_class]
        
        formatted_data.append(edited_data)

    return formatted_data
