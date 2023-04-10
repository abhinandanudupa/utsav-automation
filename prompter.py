#! /usr/bin/env python3

from pprint import pprint
from dotenv import dotenv_values
import openai

config = dotenv_values(".env")
OPEN_AI_KEY = config["OPEN_AI_KEY"]
openai.api_key = OPEN_AI_KEY

UTSAV_STUFF = "Utsav Intro"


def prompt_chatgpt(event_prompt):
    completion = openai \
        .ChatCompletion \
        .create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": event_prompt
            }]
        )
    return completion.choices[0].message.content


def generate_event_invitation_prompt(event):
    club_name = event['club']
    event_name = event['eventName']
    # mode_of_conduction = event["eventMode"]
    # venue = event['venue']
    # timings = event['eventDate']
    description = event['description']
    rules = event['rules']
    # category_info = [("competition", "judge")]
    role = 'Please note that he/she is the judge for the event'
    # coordinators = event['coordinators']

    event_prompts = []
    for judge in event['resourcePerson']:
        invitation_prompt = f"""
With the description below:
Event Name: {event_name}

Description:
{description}

Rules:
{rules}


Describe the event - {event_name} in 1 to 3 sentences. Write a short paragraph addressed to {judge['name']} on behalf 
of the club - {club_name} describing how her/his experience as {judge['role']} will be useful to the event the above 
event - {event_name}. {role}. The paragraph should not be more than 4 sentences.
        """

        event_prompts.append(invitation_prompt)
    return event_prompts


def generate_invitation_prompts(events):
    invitation_prompts = []
    for event in events:
        invitation_prompts.append(generate_event_invitation_prompt(event))

    return invitation_prompts


def generate_event_invitation_reply(event_zipped):
    event_replies = []
    event, prompts = event_zipped
    print(event['eventName'])
    for prompt in prompts:
        event_replies.append(prompt_chatgpt(prompt))

    return event_replies


def generate_all_invitation_replies(events_n_prompts_zipped):
    all_replies = []
    for event, prompts in events_n_prompts_zipped:
        reply = generate_event_invitation_reply((event, prompts))
        all_replies.append(reply)

    return all_replies


def generate_invitation_bodies(events_with_replies_zipped):
    invitation_emails = []
    for event_zipped in events_with_replies_zipped:
        event, replies = event_zipped
        # pprint(replies)
        club_name = event['club']
        event_name = event['eventName']
        mode_of_conduction = event["eventMode"]
        venue = event['venue']
        timings = event['eventDate']
        # description = event['description']
        # rules = event['rules']
        category_info = [("competition", "judge")]
        # role = 'Please note that he/she is the judge for the event'
        coordinators = event['coordinators']
        emails = []
        for reply in replies:
            email = f"""
#### {UTSAV_STUFF} ####

We are delighted to invite you to {category_info[0][1]} the event {event_name} on behalf of the club - {club_name}. 
The event will be conducted in {mode_of_conduction} mode from {timings} the {venue}.

{reply}

{coordinators[0]['name']}
{coordinators[0]['email']}
{coordinators[0]['phone']}


{coordinators[1]['name']}
{coordinators[1]['email']}
{coordinators[1]['phone']}
            """
            emails.append(email)
        invitation_emails.append(emails)
    return invitation_emails
