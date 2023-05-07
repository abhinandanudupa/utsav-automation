#! /usr/bin/env python3

import sys
import argparse
from dotenv import dotenv_values
from generators import InvitationGenerator
from csv_parsing import parse_all_files, parse_report_csv, save_inputs_as_json, save_as_csv
from pprint import pprint
config = dotenv_values(".env")
OPEN_AI_KEY = config["OPEN_AI_KEY"]


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
        default='./Events_Test/'
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
        '--outputs',
        help='save the generated replies as emails',
        action=argparse.BooleanOptionalAction,
        default=True
    )

    parser.add_argument(
        '--output-file',
        help='prompt ChatGPT with the generated prompts',
        default='generated_emails.csv'
    )

    arguments = vars(parser.parse_args(sys.argv[1:]))

    input_folder = arguments['input_folder']
    parsed_input_file = arguments['parsed_json']
    output_file = arguments['output_file']

    events = parse_all_files(input_folder)
    # pprint(events)
    save_inputs_as_json(parsed_input_file, events)

    invites = InvitationGenerator(events, OPEN_AI_KEY)

    if arguments['prompts']:
        invites.generate_prompts_for_all_events()

    if arguments['replies']:
        invites.get_replies_for_all_events()
        if arguments['outputs']:
            invites.generate_formatted_outputs_for_all_events()

    # pprint(invites.all_replies)
    # pprint(invites.all_emails)

    prompts, replies, emails = invites.zip_n_store_as_dict(
        save_prompts=arguments['prompts'],
        save_replies=arguments['replies'],
        save_outputs=arguments['outputs']
    )

    print("Saving prompts...")
    save_as_csv(prompts, arguments['prompts_file'])

    print("Saving replies...")
    save_as_csv(replies, arguments['raw_replies_file'])

    print("Saving emails...")
    save_as_csv(emails, arguments['output_file'])
