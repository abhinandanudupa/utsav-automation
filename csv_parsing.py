#! /usr/bin/env python3


from pprint import pprint
import csv
import json
import os
import fnmatch


class CSVParser:
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

    def __init__(self, input_folder_path, parsed_inputs_file, output_file):
        self.input_folder_path = input_folder_path
        self.output_file = output_file
        self.parsed_inputs_file = parsed_inputs_file
        self.file_to_parse = []

        folder_abs_path = os.path.abspath(input_folder_path)
        for file in os.listdir(input_folder_path):
            if not fnmatch.fnmatch(file, "*.csv"):
                continue
            file_full_path = os.path.join(folder_abs_path, file)
            self.file_to_parse.append(file_full_path)

    @staticmethod
    def stringify_field(field_content):
        content_str = ''
        for rule in field_content:
            content_str += f'{rule}\n'

        return content_str.strip()

    @staticmethod
    def remove_unnecessary_fields(dict_list):
        clean_dict_list = []
        for dict_obj in dict_list:
            clean_dict = {}
            for key in dict_obj:
                if key in CSVParser.FIELDS_TO_IGNORE:
                    continue
                clean_dict[key] = dict_obj[key]

            clean_dict_list.append(clean_dict)

        return clean_dict_list

    @staticmethod
    def ignore_fields(field_name):
        if field_name in CSVParser.FIELDS_TO_IGNORE:
            return True
        return False

    @staticmethod
    def is_json_obj(field_name):
        if field_name in CSVParser.JSON_FIELDS:
            return True
        return False

    @staticmethod
    def process_events(event_list):
        for event in event_list:
            for field in event:
                if field in CSVParser.FIELDS_TO_STRINGIFY:
                    event[field] = CSVParser.stringify_field(event[field])
                if field in CSVParser.FIELDS_TO_PARSE:
                    event[field] = CSVParser.remove_unnecessary_fields(event[field])

    @staticmethod
    def parse_csvfile(input_file):
        events_parsed = []
        with open(input_file, "r") as csv_file:
            csv_obj = csv.DictReader(csv_file, dialect="excel")
            for row in csv_obj:
                events_parsed.append({})
                for key in row:
                    if not CSVParser.ignore_fields(key):
                        if CSVParser.is_json_obj(key):
                            events_parsed[-1].update(
                                {key: json.loads(row[key])}
                            )
                            continue
                        events_parsed[-1].update(
                            {key: row[key]}
                        )
        return events_parsed

    def parse_all_files_in_folder(self):
        parsed_events = []
        if len(self.file_to_parse) == 0:
            print(F"No files in {self.input_folder_path}")
        for csv_file in self.file_to_parse:
            events_in_file = self.parse_csvfile(csv_file)
            self.process_events(events_in_file)
            parsed_events += events_in_file
        return parsed_events

    def save_inputs_as_json(self, event_list):
        with open(self.parsed_inputs_file, "w") as parsed_file:
            parsed_file.write(json.dumps(event_list))

    @staticmethod
    def save_as_csv(rows, file_name):
        if len(rows) == 0:
            print("No items to save!")
            return
        with open(file_name, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
