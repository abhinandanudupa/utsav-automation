#! /usr/bin/env python3

import sys
import argparse
from dotenv import dotenv_values
from generators import InvitationGenerator
from csv_parsing import CSVParser
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

    input_folder = arguments['input_folder']
    parsed_input_file = arguments['parsed_json']
    output_file = arguments['emails_file']

    csv_parser = CSVParser(input_folder, parsed_input_file, output_file)
    events = csv_parser.parse_all_files_in_folder()
    # pprint(events)
    csv_parser.save_inputs_as_json(events)

    invites = InvitationGenerator(events, OPEN_AI_KEY)

    if arguments['prompts']:
        invites.generate_prompts_for_all_events()

    if arguments['replies']:
        invites.get_replies_for_all_events()
        if arguments['emails']:
            invites.generate_formatted_outputs_for_all_events()
    # pprint(invites.all_replies)
    # pprint(invites.all_emails)
    prompts, replies, emails = invites.zip_n_store_as_dict(
        convert_prompts=arguments['prompts'],
        convert_replies=arguments['replies'],
        convert_emails=arguments['emails']
    )

    print("Saving prompts...")
    csv_parser.save_as_csv(prompts, arguments['prompts_file'])

    print("Saving replies...")
    csv_parser.save_as_csv(replies, arguments['raw_replies_file'])

    print("Saving emails...")
    csv_parser.save_as_csv(emails, arguments['emails_file'])
