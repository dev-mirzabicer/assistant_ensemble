from Assistant import Assistant
from Team import Team
from User import User
from commands import command_wrapper
from DriverWindowManager import global_driver_manager

import time
import json
import os

teammate_commands = [
    "!whisper",
    "!raisehand",
    "!list",
    "!delete",
    "!write",
    "!read",
    "!preview",
    "!run",
]

moderator_commands = [
    "!team",
    "!allowspeak",
    "whisper",
    "!list",
    "!delete",
    "!write",
    "!read",
    "!preview",
    "!run",
    "!user",
    "!note",
    "!permanentnote",
]

planner = ("Planner", teammate_commands)

time.sleep(1)
# researcher = Assistant(teammate_commands, "Researcher")
# software_engineer = Assistant(teammate_commands, "Software Engineer")
# mike = Assistant(teammate_commands, "Mike")
# academician = Assistant(teammate_commands, "Academician")

# moderator = Assistant(moderator_commands, "Moderator")
researcher = ("Researcher", teammate_commands)
software_engineer = ("Software Engineer", teammate_commands)
mike = ("Mike", teammate_commands)
academician = ("Academician", teammate_commands)

moderator = ("Moderator", moderator_commands)
time.sleep(1)

# teamlist = [planner]  # , researcher, software_engineer, mike, academician]
teamlist = [planner, researcher, software_engineer, mike, academician]

team = Team(teamlist, moderator)

for member in team.members:
    member.cmd_wrapper = command_wrapper(member, team)

team.moderator.cmd_wrapper = command_wrapper(team.moderator, team)

intro_and_inst = json.load(open("./data/user_instructions.json"))

time.sleep(1)
user = User(
    "User",
    intro_and_inst["introduction"],
    intro_and_inst["instructions"],
    team.moderator,
)

team.user = user

if __name__ == "__main__":
    team.parse_all()
    time.sleep(1)
    user.introduce()
    time.sleep(1)
    team.parse_all()
    prompt = input("Enter your first prompt: ")
    time.sleep(1)
    user.send_message(prompt)
    while prompt != "!exit":
        time.sleep(1)
        team.parse_all()
        while not user.waiting_for_response:
            time.sleep(1)
        prompt = input("Enter your next prompt: ")
        time.sleep(1)
        user.send_message(prompt)
        user.waiting_for_response = False
    global_driver_manager.close_all()
    print("Exiting...")
