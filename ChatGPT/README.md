# utsav-automation
A simple extensible Python script that uses ChatGPT to generate emails. Specify a folder containing details of events in CSV files and generate emails!

## Instructions
Just install the modules from [requirements.txt](./requirements.txt) and run as `./automate`, on Linux/MacOS and `python automate.py` on Windows.

## Options
Optionally specify the following options:

| Option                           | Explanation                                                                                                  |
| :------------------------------- | :----------------------------------------------------------------------------------------------------------- |
| `--input-folder`                 | to specify the folder where input CSV files are located, defaults to `./Events_Test/`                        |
| `--prompts`/`--no-prompts`       | to enable/disable prompt generation                                                                          |
| `--replies`/`--no-replies`       | to enable/disable requests to ChaptGPT                                                                       |
| `--emails`/`--no-emails`         | to enable/disable email generation                                                                           |
| `--prompts-file [file name]`     | to specify the name of the CSV file to store prompts, defaults to `./generated_prompts.csv`                  |
| `--raw-replies-file [file name]` | to specify the name of the CSV file to store replies from ChatGPT, defaults to `./generated_raw_replies.csv` |
| `--emails-file [file name]`      | to specify the name of the CSV file to store emails, defaults to `./generated_emails.csv`                    |

## How it works
It loads details of events from CSV files located in an input folder which you specify. It parses the details into a list of dictionary with each dictionary representing the event. It then iterates through this list of events to generate prompts with the details of the judges for ChatGPT, gets replies from ChatGPT and puts it into a email. The emails will be saved in a CSV file. It saves three CSV files - one for the prompts, one for the replies and one for the emails. Right now it can generate invitation emails but will need fine tuning ie. improving the prompt. 

## Extensions
You can specify custom prompts and emails by inheriting from the `BaseGenerator` class and overriding the functions `generate_prompts_for_event()`, where you specify the prompts and `generate_prompts_for_event()`, where you specify the email format from [generators.py](./generators.py).

