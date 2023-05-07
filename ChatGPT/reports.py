from pprint import pprint
from dotenv import dotenv_values
from generators import ReportsGenerator
from csv_parsing import parse_all_files, parse_report_csv, save_inputs_as_json, save_as_csv
import csv


config = dotenv_values(".env")
OPEN_AI_KEY = config["OPEN_AI_KEY"]


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


events = parse_report_csv("reports.csv")

reports_generator = ReportsGenerator(events, OPEN_AI_KEY)

reports_generator.extract_relevant_data()

reports_generator.generate_prompts_for_all_events()
reports_generator.get_replies_for_all_events()
reports_generator.generate_formatted_outputs_for_all_events()

prompts, replies, reports = reports_generator.zip_n_store_as_dict(
        save_prompts=True,
        save_replies=True,
        save_outputs=True
    )

# pprint(prompts)
# pprint(replies)
# pprint(reports)

