#! /usr/bin/env python3

from copy import deepcopy
from abc import ABC, abstractmethod
import openai
import traceback
import time


class BaseGenerator(ABC):
    def __init__(self, event_list, openai_api_key=None):
        self.event_list = event_list
        openai.api_key = openai_api_key
        self.all_prompts = []
        self.all_replies = []
        self.all_outputs = []
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
        time.sleep(20)
        return completion.choices[0].message.content
        # return F"Reply for {prompt}"

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
        # print(F"Prompting ChatGPT for {event[list(event.keys())[0]]}")
        event_replies = []
        for i, prompt in enumerate(event_prompts):
            try:
                reply = self.prompt_chatgpt(prompt)
                event_replies.append(reply)
            except:
                print("Failed to get a reply from ChatGPT!")
                # print(F"""Was requesting for {event[list(event.keys())[0]]} and for the judge {event['resourcePerson'][i]}.""")
                traceback.print_exc()

        self.all_replies.append(event_replies)

    # To be overloaded
    @abstractmethod
    def generate_formatted_outputs_for_event(self, event, event_replies):
        UTSAV_INTRO = "Utsav Intro"
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
            email = F"""#### {something} ####"""
            event_emails.append(email)
        # INFO: Make sure you update the all_emails variable
        self.all_outputs.append(event_emails)

    def generate_prompts_for_all_events(self):
        for event in self.event_list:
            self.generate_prompts_for_event(event)

    def get_replies_for_all_events(self):
        for event, event_prompts in zip(self.event_list, self.all_prompts):
            self.get_replies_for_event(event, event_prompts)

    def generate_formatted_outputs_for_all_events(self):
        for event, event_replies in zip(self.event_list, self.all_replies):
            print(F"Generating outputs for {event[list(event.keys())[0]]}")
            self.generate_formatted_outputs_for_event(event, event_replies)

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

    @abstractmethod
    def zip_n_store_as_dict(self, save_prompts=True, save_replies=True, save_outputs=True):
        prompt_data, reply_data, output_data = [], [], []
        if save_prompts:
            events_n_prompts = zip(self.event_list, self.all_prompts)
            for i, (event, prompts) in enumerate(events_n_prompts):
                for prompt in prompts:
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "prompt": prompt
                    })
                    prompt_data.append(data)

        if save_replies:
            events_n_replies = zip(self.event_list, self.all_replies)
            for i, (event, replies) in enumerate(events_n_replies):
                for reply in replies:
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "reply": reply
                    })
                    reply_data.append(data)

        if save_outputs:
            events_n_outputs = zip(self.event_list, self.all_outputs)
            for i, (event, outputs) in enumerate(events_n_outputs):
                for output in outputs:
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "output": output,
                    })
                    output_data.append(data)
        return prompt_data, reply_data, output_data


class InvitationGenerator(BaseGenerator, ABC):
    def generate_prompts_for_event(self, event):
        print(F"Generating prompts for {event[list(event.keys())[0]]}")
        club_name = event['club']
        event_name = event['eventName']
        description = event['description']
        rules = event['rules']
        role = 'Please note that he/she is the judge for the event'

        prompts = []
        for judge in event['resourcePerson']:
            prompt = F"""
With this description of the competition below:
Event Name: {event_name}

Description:
{description}

Rules:
{rules}


You are a an invitation letter writing AI. You task is to write emails to judges inviting them to the event mentioned above which is a part of a college cultural fest.

Write the following two paragraphs for a letter:
Write a very short one sentence introduction to the event above with the given information, conveying the essence of the game.

Follow it up with a short paragraph, addressed to {judge['name']}, {judge['role']}, inviting him/her to judge this competition on behalf of the {club_name} by stating the name, venue, timings with full date of the competition from above. State how her experience as a {judge['role']} will be useful for judging this competition.

These are the requirements:

- Please make it formal and appealing to the reader and note that the text you output will be a part of an partially complete email.
- Be explicit that you are inviting on behalf of the club.
- She has confirmed her presence for the event.
- Each paragraph must not be more than 3 sentences.
"""
            prompts.append(prompt)
        self.all_prompts.append(prompts)

    def generate_formatted_outputs_for_event(self, event, event_replies):
        UTSAV_INTRO = "INTRO"
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
        self.all_outputs.append(event_emails)

    def zip_n_store_as_dict(self, save_prompts=True, save_replies=True, save_outputs=True):
        prompt_data, reply_data, email_data = [], [], []
        if save_prompts:
            events_n_prompts = zip(self.event_list, self.all_prompts)
            for i, (event, prompts) in enumerate(events_n_prompts):
                for prompt in prompts:
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "reply": prompt
                    })
                    prompt_data.append(data)

        if save_replies:
            events_n_replies = zip(self.event_list, self.all_replies)
            for i, (event, replies) in enumerate(events_n_replies):
                for reply in replies:
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "reply": reply
                    })
                    reply_data.append(data)

        if save_outputs:
            events_n_emails = zip(self.event_list, self.all_outputs)
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


class ReportsGenerator(BaseGenerator, ABC):

    def generate_prompts_for_event(self, event):
        print(F"Generating prompts for {event['Event Name']}")
        event_name = event['Event Name']
        description = event['Description of Event']
        winners = event['Winner(s) and Prize']
        dates = event['Date(s)']
        judges = event['Judge(s) and Designation'].split('\n')

        prompt = F"""
With this description of the competition below:
Event Name: {event_name}

Description:
{description}

Judges:
{judges}

Date: {dates}

Winners and prize:
{winners}

You are a report writing AI. You task is to write reports about the events conducted in a college cultural fest.

Write a report paragraph that answers these questions:
What exactly was the event about and its purpose? (3-4 lines)
How many teams of/ participants took part?
Where was the event conducted? (ie: venue)
What were the various rounds and rules in the event and how did the teams progress through these rounds? (5-6 lines)
How did the event conclude and what was the feedback of the participants? (3-4 lines)
Who are the winners of the event?
Who and what were the accomplishments and roles of the judges in the competition?

Make sure that this description is no more than 15 sentences long.
        """
        self.all_prompts.append([prompt])

    def generate_formatted_outputs_for_event(self, event, event_replies):
        self.all_outputs.append([event_replies])

    def get_relevant_data_from_event(self, event_dict):
        return deepcopy(event_dict)

    def zip_n_store_as_dict(self, save_prompts=True, save_replies=True, save_outputs=True):
        prompt_data, reply_data, output_data = [], [], []
        if save_prompts:
            events_n_prompts = zip(self.event_list, self.all_prompts)
            for i, (event, prompts) in enumerate(events_n_prompts):
                for prompt in prompts:
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "prompt": prompt
                    })
                    prompt_data.append(data)

        if save_replies:
            events_n_replies = zip(self.event_list, self.all_replies)
            for i, (event, replies) in enumerate(events_n_replies):
                for reply in replies:
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "reply": reply
                    })
                    reply_data.append(data)

        if save_outputs:
            events_n_reports = zip(self.event_list, self.all_outputs)
            for i, (event, reports) in enumerate(events_n_reports):
                for report in reports:
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "report": report,
                    })
                    output_data.append(data)

        return prompt_data, reply_data, output_data

