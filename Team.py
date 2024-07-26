from Assistant import Assistant
from uuid import uuid4
import os
import json


class Team:
    def __init__(self, members, moderator, user=None):
        self.user = user
        # self.members = members
        self.session_id = uuid4()
        # create file, in a directory specific to the team
        os.mkdir(f"./team_folders/{self.session_id}")
        with open(f"./team_folders/{self.session_id}/team_chat.txt", "w") as f:
            f.write("Team Chat\n")
        os.mkdir(f"./team_folders/{self.session_id}/filebase")

        # ./data/instructions.json
        instructions = json.load(open("./data/instructions.json"))
        teammate_instructions = json.load(open("./data/teammate_instructions.json"))

        initial_message = f"{instructions["main"]["instructions"]}\nYour team is: {instructions["main"]["team"]}\nCommands: {instructions["main"]["commands"]}\nImportant: {instructions["main"]["warnings"]}\nTools: {instructions["tools"]}\nNote: Google tool is not ready yet."
        self.moderator = Assistant(moderator[1], moderator[0])

        future = self.moderator.agent.send_message(initial_message)
        # wait for the message to be sent
        future.result()

        # self.moderator.agent.get_latest_response().result()

        teammate_messages = f"{teammate_instructions["main"]}\nYour team is: {instructions["main"]["team"]}\n{teammate_instructions["role_explanation"]}\nImportant: {teammate_instructions["rules"]}\nCommands: {teammate_instructions["commands"]}\nTools: {instructions["tools"]}\nNote: Google tool is not ready yet."
        self.members = [Assistant(cmds, name) for name, cmds in members]
        for member in self.members:
            future = member.agent.send_message(teammate_messages.replace("<NAME>", member.name))
            # wait for the message to be sent
            future.result()
            # member.agent.get_latest_response().result()

    def message(self, member: Assistant, message):
        for m in self.members:
            if m != member:
                m.get_team_message(member.name, message)
        if self.moderator != member:
            self.moderator.get_team_message(member.name, message)
        with open(f"./team_folders/{self.session_id}/team_chat.txt", "a") as f:
            f.write(f"{member.name}: {message}\n")
    
    def parse_all(self):
        for member in self.members:
            member.parse_response()
        self.moderator.parse_response()
    
    def whisper(self, sender: Assistant, message, receiver_name):
        # Strip and remove curly brackets
        message = message.strip().replace("{", "").replace("}", "")
        for member in self.members:
            if member.name == receiver_name:
                member.get_whisper(sender.name, message)
                with open(f"./team_folders/{self.session_id}/team_chat.txt", "a") as f:
                    f.write(f"{sender.name} whispered to {receiver_name}: {message}\n")
                return
        self.moderator.agent.send_message(f"Couldn't find {receiver_name} in the team.").result(timeout=300)
    
    def let_allowance(self, agent_name):
        for member in self.members:
            if member.name == agent_name:
                member.get_allowance()
                return
        return f"Couldn't find {agent_name} in the team."
    
    def message_user(self, agent_name, message):
        if self.moderator.name == agent_name:
            self.user.get_message(message)
        else:
            self.user.get_message(f"{agent_name} said: {message}")
        
