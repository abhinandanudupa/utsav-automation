#! /usr/bin/env python3


from pprint import pprint
import csv
import json
import os
import fnmatch


FIELDS_TO_IGNORE = [
    '__v',
    '_id',
    'createdAt',
    'eventParticipation',
    'ieeeRegFee',
    'imageurl',
    'isIEEE',
    'lastRegDate',
    'posterLink',
    'prize',
    'regFee',
    'sponsorsDetails',
    'spreadsheetId',
    'stopallregs',
    'stoponlineregs',
    'stopspotregs',
    'updatedAt',
    'image'
]

JSON_FIELDS = [
    'rules',
    'resourcePerson',
    'eventType',
    'coordinators'
]

FIELDS_TO_STRINGIFY = [
    'rules'
]

FIELDS_TO_PARSE = [
    'resourcePerson',
    'coordinators'
]


def stringify_field(field_content):
    content_str = ''
    for rule in field_content:
        content_str += f'{rule}\n'

    return content_str.strip()


def remove_unnecessary_fields(dict_list):
    clean_dict_list = []
    for dict_obj in dict_list:
        clean_dict = {}
        for key in dict_obj:
            if key in FIELDS_TO_IGNORE:
                continue
            clean_dict[key] = dict_obj[key]

        clean_dict_list.append(clean_dict)

    return clean_dict_list


def ignore_fields(field_name):
    if field_name in FIELDS_TO_IGNORE:
        return True
    return False


def is_json_object(field_name):
    if field_name in JSON_FIELDS:
        return True
    return False


def process_events(event_list):
    for event in event_list:
        for field in event:
            if field in FIELDS_TO_STRINGIFY:
                event[field] = stringify_field(event[field])
            if field in FIELDS_TO_PARSE:
                event[field] = remove_unnecessary_fields(event[field])


def parse_csvfile(input_file):
    events_parsed = []
    with open(input_file, "r") as csv_file:
        csv_obj = csv.DictReader(csv_file, dialect="excel")
        for row in csv_obj:
            events_parsed.append({})
            for key in row:
                if not ignore_fields(key):
                    if is_json_object(key):
                        events_parsed[-1].update(
                            {key: json.loads(row[key])}
                        )
                        continue
                    events_parsed[-1].update(
                        {key: row[key]}
                    )
    return events_parsed


def save_inputs_as_json(parsed_inputs_file, event_list):
    with open(parsed_inputs_file, "w") as parsed_file:
        parsed_file.write(json.dumps(event_list))


def save_as_csv(rows, file_name):
    if len(rows) == 0:
        print("No items to save!")
        return
    with open(file_name, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def find_csv_files(input_folder_path):
    files_to_parse = []
    folder_abs_path = os.path.abspath(input_folder_path)
    for file in os.listdir(input_folder_path):
        if not fnmatch.fnmatch(file, "*.csv"):
            continue
        file_full_path = os.path.join(folder_abs_path, file)
        files_to_parse.append(file_full_path)
    return files_to_parse


def parse_all_files(folder_path):
    files_to_parse = find_csv_files(folder_path)
    parsed_events = []
    if len(files_to_parse) == 0:
        print(F"No files in {folder_path}")
    for csv_file in files_to_parse:
        events_in_file = parse_csvfile(csv_file)
        process_events(events_in_file)
        parsed_events += events_in_file
    return parsed_events


def parse_report_csv(report_csv):
    parsed_details = []
    start_off_set = 4
    columns_for_event = 5
    num_events = 2
    with open(report_csv, 'r') as csv_file:
        csv_obj = csv.reader(csv_file)
        headers = []
        for index, row in enumerate(csv_obj):
            if index == 0:
                headers = row[start_off_set:start_off_set + columns_for_event]
                continue

            for i in range(num_events):
                event_offset = start_off_set + (i * columns_for_event)
                event_data = row[event_offset: event_offset + columns_for_event]
                parsed_details.append({"Club Name": row[2]})
                for field, content in zip(headers, event_data):
                    if len(content.strip()) != 0:
                        parsed_details[-1].update({field: content})
    return parsed_details
