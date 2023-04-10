#! /usr/bin/env python3


# from pprint import pprint
import csv
import json


FIELDS_TO_IGNORE = [
    '__v',
    '_id',
    'createdAt',
    'eventId',
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


def ignore_fields(field_name):
    if field_name in FIELDS_TO_IGNORE:
        return True
    return False


def is_json_obj(field_name):
    if field_name in JSON_FIELDS:
        return True
    return False


def parse_csvfile(file_path):
    events_parsed = []
    with open(file_path, "r") as csv_file:
        csv_obj = csv.DictReader(csv_file, dialect="excel")
        for row in csv_obj:
            events_parsed.append({})
            for key in row:
                if not ignore_fields(key):
                    if is_json_obj(key):
                        events_parsed[-1].update(
                            {key: json.loads(row[key])}
                        )
                        continue
                    events_parsed[-1].update(
                        {key: row[key]}
                    )
    return events_parsed


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


def process_events(event_list):
    for event in event_list:
        for field in event:
            if field in FIELDS_TO_STRINGIFY:
                event[field] = stringify_field(event[field])
            if field in FIELDS_TO_PARSE:
                event[field] = remove_unnecessary_fields(event[field])


def save_inputs(file_name, event_list):
    with open(file_name, "w") as parsed_file:
        parsed_file.write(json.dumps(event_list))


def save_as_csv(filename, rows):
    with open(filename, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
