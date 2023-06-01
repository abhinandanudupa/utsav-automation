#! /usr/bin/env python3
import json
from copy import deepcopy
from abc import ABC, abstractmethod
import openai
import traceback
import time
from dotenv import dotenv_values


config = dotenv_values(".env")
OPEN_AI_KEY = config["OPEN_AI_KEY"]
openai.api_key = OPEN_AI_KEY


class BaseGenerator(ABC):
    def __init__(self, event_list, openai_api_key=None):
        self.event_list = event_list
        self.all_prompts = []
        self.all_replies = []
        self.all_outputs = []
        self.event_relevant_data = []
        self.extract_relevant_data()

    @staticmethod
    def prompt_chatgpt(prompt):
        # completion = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{
        #         "role": "user",
        #         "content": prompt
        #     }]
        # )
        # print("Sleeping for 20s...")
        # time.sleep(20)
        # return completion.choices[0].message.content
        return F"Reply for {prompt}"

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
    def __init__(self, event_list, openai_api_key=None, rp_details='parsed_rp_details.json'):
        super().__init__(event_list, openai_api_key)
        self.rp_details = {}
        with open(rp_details, 'r') as f:
            content = f.read()
            self.rp_details = json.loads(content)

    def generate_prompts_for_event(self, event):
        print(F"Generating prompts for {event[list(event.keys())[0]]}")
        club_name = event['club']
        event_name = event['eventName']
        description = event['description']
        rules = event['rules']
        venue = event['venue']
        date_and_timings = event['eventDate']
        mode = event['eventMode']
        event_id = event['eventId'].strip()

        prompts = []
        for judge in self.rp_details.get(event_id, []):
            prompt = F"""
With this description of the competition below:
Event Name: {event_name}

Mode: {mode}

Date and Timings: {date_and_timings}

Venue: {venue}

Description:
{description}

Rules:
{rules}

Resource Person:
{judge['name']}

Experience:
{judge['brief_description']}

And this description of UTSAV 2023:

Utsav - the Festival of Faith - is a grand cultural fest hosted by B M S College of Engineering in Bengaluru. Over the years, Utsav has established itself as a brand, and has become one of the biggest and most popular cultural fests hosted by any college in Bengaluru, providing an invaluable platform to explore one's talents and artistic endeavours in areas such as music, dance, literature, theatre, and more.

Passionate students are given ample opportunities to express themselves and compete with one another, with creativity, courage, and persistence being rewarded generously at Utsav. Drawing participants from all over India, the festival has set new benchmarks with its events on numerous occasions, making it an unforgettable experience for years to come.

Utsav is a landmark celebration, and has been admired for its dedication to beat with the rhythms of cosmopolitan Bengaluru. Standing tall since 1981, this mega-event has earned a distinguished reputation in South India for not only being a thriving hub of cultural excellence but also for warmly embracing everyone, regardless of any barriers. Coming at no cost, this student fest draws in crowds like moths to flame.

This year, with the theme of "Regalia", the bar can only be set higher, and we eagerly await your participation in this extraordinary cultural celebration.

Theme:
Regalia emulates royalty - it is not just an emotion, but a way of life that makes one feel a sense of belonging while also being in an exalted state of being. Regality is experienced by those who give their all, stand firm for what they believe in, and have faith in their purpose, like flowers that bloom through concrete. It does not require material possessions or money, but can be found in one's passion, vigour, and drive to achieve their dreams. When someone is driven by a strong sense of purpose and a burning desire to succeed, they radiate a regal aura that commands respect, admiration and reverence. In essence, true royalty is not about what one possesses, but rather about who they are and what they stand for.

Utsav 2023 aims to uplift and nurture the light within us by celebrating our unique talents, strengths, and individuality. Fondly and aptly known as the Festival of Faith, Utsav is spotlighting the indomitable human spirit in its 2023 edition. 


You are a an invitation letter writing AI. You task is to write emails to judges inviting them to the event mentioned above which is a part of a college cultural fest.

Write the following two paragraphs for a letter:
Write a very short one sentence introduction to the event above with the given information, conveying the essence of the game.

Follow it up with a short paragraph, addressed to {judge['name']}, inviting him/her to judge this competition on behalf of the {club_name} by stating the name, venue, timings with full date of the competition from above. State how her experience as a judge will be useful for judging this competition.

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
        event_id = event['eventId'].strip()
        # description = event['description']
        # rules = event['rules']
        # category_info = [("competition", "judge")]
        # role = 'Please note that he/she is the judge for the event'
        coordinators = event['coordinators']
        event_emails = []
        for judge, reply in zip(self.rp_details.get(event_id, []), event_replies):
            email = F"""
#### {UTSAV_INTRO} ####

We are delighted to invite you to judge the event {event_name} on behalf of the club - {club_name}. 
The event will be conducted in {mode_of_conduction} mode from {timings} at {venue}.

{reply}

{coordinators[0]['name']}
{coordinators[0]['email']}
{coordinators[0]['phone']}

"""

# {coordinators[1]['name']}
# {coordinators[1]['email']}
# {coordinators[1]['phone']}
# """
            event_emails.append(email)
        self.all_outputs.append(event_emails)

    def zip_n_store_as_dict(self, save_prompts=True, save_replies=True, save_outputs=True):
        prompt_data, reply_data, email_data = [], [], []
        if save_prompts:
            events_n_prompts = zip(self.event_list, self.all_prompts)
            for i, (event, prompts) in enumerate(events_n_prompts):
                for prompt, rp_details in zip(prompts, self.rp_details.get(event['eventId'], [])):
                    rp_name = rp_details['name']
                    rp_email = rp_details['email_id']
                    desc = rp_details['brief_description']
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "prompt": prompt,
                        "email": rp_email
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
                for email, rp_details in zip(emails, self.rp_details.get(event['eventId'], [])):
                    rp_name = rp_details['name']
                    desc = rp_details['brief_description']
                    data = deepcopy(self.event_relevant_data[i])
                    data.update({
                        "invitation": email,
                        "name": rp_name,
                        "brief_description": desc
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

