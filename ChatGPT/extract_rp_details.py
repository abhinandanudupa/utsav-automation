from pprint import pprint
# from dotenv import dotenv_values
from generators import ReportsGenerator
from csv_parsing import (
    parse_all_files,
    parse_report_csv,
    save_inputs_as_json,
    save_as_csv,
)
import csv


def parse_report_csv(report_csv):
    parsed_details = []
    start_off_set = 5
    columns_for_event = 4
    num_events = 3
    with open(report_csv, "r") as csv_file:
        csv_obj = csv.reader(csv_file)
        headers = []
        for index, row in enumerate(csv_obj):
            if index == 0:
                headers = row[start_off_set : start_off_set + columns_for_event]
                continue

            for i in range(num_events):
                event_offset = start_off_set + (i * columns_for_event)
                event_data = row[event_offset:event_offset + columns_for_event]
                parsed_details.append({"eventCode": row[3]})
                for field, content in zip(headers, event_data):
                    if len(content.strip()) != 0:
                        parsed_details[-1].update({field.lower().replace(' ', '_'): content})

        non_empty_details = []
        for event in parsed_details:
            if event.get('phone_number', False):
                non_empty_details.append(event)

    return non_empty_details


rp_details = parse_report_csv("rp_details.csv")
pprint(rp_details)

consolidated = {}
for rp in rp_details:
    event_code = rp['eventCode']
    consolidated[event_code] = consolidated.get(event_code,  [])
    consolidated[event_code].append(rp)


pprint(consolidated)

save_as_csv(rp_details, 'parsed_rp_details.json')

