#! /usr/bin/env python3

# from pprint import pprint
from copy import deepcopy
import os
import sys
import argparse
import fnmatch
import csv_parsing
import prompter


def parse_all_files_in_folder(folder_path):
    folder_abs_path = os.path.abspath(folder_path)
    parsed_events = []
    for file in os.listdir(folder_path):
        if not fnmatch.fnmatch(file, "*.csv"):
            continue
        file_full_path = os.path.join(folder_abs_path, file)
        events_in_file = csv_parsing.parse_csvfile(file_full_path)
        csv_parsing.process_events(events_in_file)
        parsed_events += events_in_file
    return parsed_events


def get_relevant_info_from_event(event_dict):
    club_name = event_dict['club']
    event_name = event_dict['eventName']
    mode_of_conduction = event_dict["eventMode"]
    venue = event_dict['venue']
    timings = event_dict['eventDate']
    description = event_dict['description']
    rules = event_dict['rules']
    coordinators = event_dict['coordinators']

    return {
        "club_name": club_name,
        "event_name": event_name,
        "mode_of_conduction": mode_of_conduction,
        "venue": venue,
        "timings": timings,
        "description": description,
        "rules": rules,
        "coordinators": coordinators
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='automation',
        description='Automate the boring stuff!',
        epilog='By the Admin Team of Utsav 2023'
    )

    # TODO: Change the default event folder
    parser.add_argument(
        '--input-folder',
        type=str,
        default='./Events/'
    )  # positional argument

    parser.add_argument(
        '--parsed-json',
        help='the name of the JSON file where the raw parsed JSON event list is stored',
        default='parsed_from_csv.json'
    )

    parser.add_argument(
        '--prompts',
        help='only parse the CSV file to generate the JSON file but don\'t generate prompts and don\'t prompt ChatGPT',
        action=argparse.BooleanOptionalAction,
        default=True
    )

    parser.add_argument(
        '--prompts-file',
        help='generate and save prompts to the file indicated',
        default='generated_prompts.csv'
    )

    parser.add_argument(
        '--replies',
        help='save the raw replies generated',
        action=argparse.BooleanOptionalAction,
        default=True
    )

    parser.add_argument(
        '--raw-replies-file',
        help='generate and save prompts to the file indicated',
        default='generated_raw_replies.csv'
    )

    parser.add_argument(
        '--emails',
        help='save the generated replies as emails',
        action=argparse.BooleanOptionalAction,
        default=True
    )

    parser.add_argument(
        '--emails-file',
        help='prompt ChatGPT with the generated prompts',
        default='generated_emails.csv'
    )

    arguments = vars(parser.parse_args(sys.argv[1:]))

    events = parse_all_files_in_folder(arguments['input_folder'])
    csv_parsing.save_inputs(arguments['parsed_json'], events)
    print(f'Parsed data stored in {arguments["parsed_json"]}.')

    # PROMPTS
    if not arguments['prompts']:
        exit()

    event_relevant_data = []
    for event in events:
        event_relevant_data.append(get_relevant_info_from_event(event))

    all_prompts = prompter.generate_invitation_prompts(events)

    prompt_data = []
    for i, event_prompts in enumerate(all_prompts):
        for email in event_prompts:
            data = deepcopy(event_relevant_data[i])
            data.update({
                "prompt": email
            })
            prompt_data.append(data)
    csv_parsing.save_as_csv(arguments['prompts_file'], prompt_data)
    print(f"Prompt data stored in {arguments['prompts_file']}.")

    # REPLIES
    if not arguments['replies']:
        exit()

    events_n_prompts_zipped = zip(events, all_prompts)
    # for zipped in events_n_prompts_zipped:
    #     pprint(zipped)

    all_replies = prompter.generate_all_invitation_replies(events_n_prompts_zipped)
    events_n_replies_zipped = zip(events, all_replies)
    # for event, zipped in events_n_replies_zipped:
    #     pprint(zipped)

    reply_data = []
    for i, event_replies in enumerate(all_replies):
        for email in event_replies:
            data = deepcopy(event_relevant_data[i])
            data.update({
                "reply": email
            })
            reply_data.append(data)
    csv_parsing.save_as_csv(arguments['raw_replies_file'], reply_data)
    print(f"Raw replies stored in {arguments['raw_replies_file']}.")

    # EMAILS
    if not arguments['emails']:
        exit()

    all_emails = prompter.generate_invitation_bodies(events_n_replies_zipped)
    events_n_emails_zipped = zip(events, all_emails)

    email_data = []
    for i, event_emails in enumerate(all_replies):
        for email in event_emails:
            data = deepcopy(event_relevant_data[i])
            data.update({
                "email": email
            })
            email_data.append(data)
    csv_parsing.save_as_csv(arguments['emails_file'], email_data)
    print(f"Emails stored in {arguments['emails_file']}.")

    # for event, zipped in events_n_emails_zipped:
    #     pprint(zipped)
