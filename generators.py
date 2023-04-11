#! /usr/bin/env python3

from dotenv import dotenv_values
from copy import deepcopy
import openai

config = dotenv_values(".env")
OPEN_AI_KEY = config["OPEN_AI_KEY"]
openai.api_key = OPEN_AI_KEY

UTSAV_STUFF = "Utsav Intro"


class BaseGenerator:
    def __init__(self, event_list, openai_configured_lib=openai):
        self.event_list = event_list
        self.openai_configured_lib = openai_configured_lib
        self.all_prompts = []
        self.all_replies = []
        self.all_emails = []
        self.event_relevant_data = []
        self.extract_relevant_data()

    def prompt_chatgpt(self, prompt):
        completion = self.openai_configured_lib.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return completion.choices[0].message.content

    # To be overloaded
    def generate_prompts_for_event(self, event):
        # club_name = event['club']
        # event_name = event['eventName']
        # mode_of_conduction = event["eventMode"]
        # venue = event['venue']
        # timings = event['eventDate']
        # description = event['description']
        # rules = event['rules']
        # category_info = [("competition", "judge")]
        # role = 'Please note that he/she is the judge for the event'
        # coordinators = event['coordinators']
        prompt = F"PROMPT FORMAT"
        return [prompt]

    def generate_reply_for_event(self, event):
        print(event['eventName'])
        prompts = self.generate_prompts_for_event(event)
        self.all_prompts.append(prompts)

        event_replies = []
        for prompt in prompts:
            event_replies.append(self.prompt_chatgpt(prompt))
        self.all_replies.append(event_replies)
        return event_replies

    # To be overloaded
    def generate_emails_for_event(self, event, event_replies):
        # club_name = event['club']
        # event_name = event['eventName']
        # mode_of_conduction = event["eventMode"]
        # venue = event['venue']
        # timings = event['eventDate']
        # description = event['description']
        # rules = event['rules']
        # category_info = [("competition", "judge")]
        # role = 'Please note that he/she is the judge for the event'
        # coordinators = event['coordinators']
        event_emails = []
        # INFO: do what ever you want
        for something in zip([event], event_replies):
            email = F"""#### {UTSAV_STUFF} #### {something} """
            event_emails.append(email)
        return event_emails

    def generate_replies_for_all_events(self):
        for event in self.event_list:
            print(F"Getting reply from ChatGPT for {event['eventName']}")
            self.generate_reply_for_event(event)

    def generate_emails_for_all_events(self):
        for event, event_replies in zip(self.event_list, self.all_replies):
            print(F"Generating emails for {event['eventName']}")
            emails = self.generate_emails_for_event(event, event_replies)
            self.all_emails.append(emails)

    @staticmethod
    def get_relevant_data_from_event(event_dict):
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

    def extract_relevant_data(self):
        for event in self.event_list:
            self.event_relevant_data.append(self.get_relevant_data_from_event(event))

    def zip_n_store_as_dict(self, convert_prompts=True, convert_replies=True, convert_emails=True):
        prompt_data, reply_data, email_data = [], [], []
        if convert_prompts:
            events_n_prompts = zip(self.event_list, self.all_prompts)
            for i, (event, prompts) in enumerate(events_n_prompts):
                for prompt in prompts:
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "reply": prompt
                    })
                    prompt_data.append(data)

        if convert_replies:
            events_n_replies = zip(self.event_list, self.all_replies)
            for i, (event, replies) in enumerate(events_n_replies):
                for reply in replies:
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "reply": reply
                    })
                    reply_data.append(data)

        if convert_emails:
            events_n_emails = zip(self.event_list, self.all_emails)
            for i, (event, emails) in enumerate(events_n_emails):
                for email, rp_details in zip(emails, event['resourcePerson']):
                    rp_name = rp_details['name']
                    rp_role = rp_details['role']
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "invitation": email,
                        "name": rp_name,
                        "role": rp_role
                    })
                    email_data.append(data)
        return prompt_data, reply_data, email_data


class InvitationGenerator(BaseGenerator):
    def generate_prompts_for_event(self, event):
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

        prompts = []
        for judge in event['resourcePerson']:
            prompt = F"""
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
            prompts.append(prompt)

        return prompts

    def generate_emails_for_event(self, event, event_replies):
        print(F"Generating emails for {event['eventName']}")
        club_name = event['club']
        event_name = event['eventName']
        mode_of_conduction = event["eventMode"]
        venue = event['venue']
        timings = event['eventDate']
        # description = event['description']
        # rules = event['rules']
        # category_info = [("competition", "judge")]
        # role = 'Please note that he/she is the judge for the event'
        coordinators = event['coordinators']
        event_emails = []
        for judge, reply in zip(event['resourcePerson'], event_replies):
            email = F"""
#### {UTSAV_STUFF} ####

We are delighted to invite you to judge the event {event_name} on behalf of the club - {club_name}. 
The event will be conducted in {mode_of_conduction} mode from {timings} the {venue}.

{reply}

{coordinators[0]['name']}
{coordinators[0]['email']}
{coordinators[0]['phone']}


{coordinators[1]['name']}
{coordinators[1]['email']}
{coordinators[1]['phone']}
"""
            event_emails.append(email)
        return event_emails
