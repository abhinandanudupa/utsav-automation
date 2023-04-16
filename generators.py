#! /usr/bin/env python3

from copy import deepcopy
from abc import ABC, abstractmethod
import openai

UTSAV_INTRO = "Utsav Intro"


class BaseGenerator(ABC):
    def __init__(self, event_list, openai_api_key=None):
        self.event_list = event_list
        openai.api_key = openai_api_key
        self.all_prompts = []
        self.all_replies = []
        self.all_emails = []
        self.event_relevant_data = []
        self.extract_relevant_data()

    @staticmethod
    def prompt_chatgpt(prompt):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return completion.choices[0].message.content

    # To be overloaded
    @abstractmethod
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

    def get_replies_for_event(self, event, event_prompts):
        print(F"Prompting ChatGPT for {event['eventName']}")
        event_replies = []
        for i, prompt in enumerate(event_prompts):
            try:
                reply = self.prompt_chatgpt(prompt)
                event_replies.append(reply)
            except:
                print("Failed to get a reply from ChatGPT!")
                print(F"""Was requesting for {event['eventName']} and for the judge {event['resourcePerson'][i]}.""")
        if len(event_replies):
            print(F"All requests for {event['eventName']} have failed.")
        self.all_replies.append(event_replies)

    # To be overloaded
    @abstractmethod
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
        # INFO: Iterate through the replies to generate emails
        for something in event_replies:
            email = F"""#### {UTSAV_INTRO} #### {something} """
            event_emails.append(email)
        # INFO: Make sure you update the all_emails variable
        self.all_emails.append(event_emails)

    def generate_prompts_for_all_events(self):
        for event in self.event_list:
            self.generate_prompts_for_event(event)

    def get_replies_for_all_events(self):
        for event, event_prompts in zip(self.event_list, self.all_prompts):
            self.get_replies_for_event(event, event_prompts)

    def generate_emails_for_all_events(self):
        for event, event_replies in zip(self.event_list, self.all_replies):
            print(F"Generating emails for {event['eventName']}")
            self.generate_emails_for_event(event, event_replies)

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
        print(F"Generating prompts for {event['eventName']}")
        club_name = event['club']
        event_name = event['eventName']
        description = event['description']
        rules = event['rules']
        role = 'Please note that he/she is the judge for the event'

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
        self.all_prompts.append(prompts)

    def generate_emails_for_event(self, event, event_replies):
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
#### {UTSAV_INTRO} ####

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
        self.all_emails.append(event_emails)
