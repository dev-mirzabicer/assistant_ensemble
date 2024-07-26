from model_crawlers.ClaudeInterface import ClaudeInterface
import time
import re


def remove_exclamations_in_braces(text):
    def remove_exclamations(match):
        return re.sub(r"!", "", match.group())

    pattern = r"\{[^{}]*\}"
    return re.sub(pattern, remove_exclamations, text)


def extract_curly_braces(text):
    pattern = r"\{([^}]*)\}"
    matches = re.findall(pattern, text)
    return matches


class Assistant:
    def __init__(self, commands, name, cmd_wrapper=None, intro_message=None):
        self.agent = ClaudeInterface()
        self.agent.enter_to_base_url()
        # time.sleep(30)
        if intro_message is not None:
            self.agent.send_message(intro_message)
        self.commands = commands
        self.name = name
        self.cmd_wrapper = cmd_wrapper

    def parse_response(self):
        future = self.agent.get_latest_response()
        try:
            res = future.result(timeout=300)
            if res is None:
                raise Exception(
                    f"Couldn't retrieve response from Claude for {self.name}"
                )
        except Exception as e:
            raise Exception(
                f"Error getting response from Claude for {self.name}: {str(e)}"
            )
        # if res[0] != "!" and res[0] == "%":
        #     self.agent.send_message(
        #         "Please provide a command from the list given to you. Commands are prefixed with '!'. If you're trying to talk with `%`, receiving this message means you tried to talk without getting allowance."
        #     ).result(timeout=300)
        #     time.sleep(1)
        #     return self.parse_response()
        # elif res[0] != "!":
        #     self.agent.send_message(
        #         "Please provide a command from the list given to you. Commands are prefixed with '!'. If you're trying to say something, again, use one of the messaging commands."
        #     ).result(timeout=300)
        #     time.sleep(1)
        #     return self.parse_response()
        if res == "!OK":
            return True
        # Example response: "!whisper {Person} {Message}" (the curly braces are actually in the response)
        # Example with multiple commands in one response: "!whisper {Person} {Message} !msg_team {Message}" or it can be like "!whisper {Person} {Message}\n!msg_team {Message}"
        res = remove_exclamations_in_braces(res)
        # start res from the first found `!`
        print(res[: res.find("!")])
        res = res[res.find("!") :]
        commands_in_response = res.split("!")
        command_returns_list = []
        for command in commands_in_response:
            if command == "":
                continue
            thecmd = "!" + command.split(" ")[0]
            if thecmd[0] == thecmd[1] == "!":
                thecmd = thecmd[1:]
            if thecmd not in self.commands:
                self.agent.send_message(
                    f"Command '{thecmd}' is not recognized. Please provide a valid command."
                ).result(timeout=300)
                time.sleep(1)
                return self.parse_response()
            # args = re.findall(r"{(.*?)}", res)
            args = extract_curly_braces(command)
            command_returns = self.cmd_wrapper(thecmd, *args)
            command_returns_list.append(command_returns)
        if len(command_returns_list) > 0:
            self.agent.send_message(command_returns_list).result(timeout=300)
        else:
            return True
        continue_conversation = (
            self.agent.get_latest_response().result(timeout=300) != "!OK"
        )
        # continue_conversation = continue_conversation_future.result(timeout=300)
        if continue_conversation:
            time.sleep(1)
            return self.parse_response()
        return True

    def get_whisper(self, assistant_name, message):
        future = self.agent.send_message(
            f"{assistant_name} Whispered to you: {message}"
        )
        future.result(timeout=300)
        time.sleep(1)
        self.parse_response()

    def get_team_message(self, assistant_name, message):
        self.agent.send_message(
            f"{assistant_name} sent a message to the team: {message}"
            + "\n"  # + # You can either keep listening by responding with `!OK`, or you can raise your hand to speak by typing `!raisehand`. If you want to execute another command by yourself, you can do that too.
        ).result(timeout=300)
        time.sleep(1)
        # self.parse_response()

    def get_allowance(self):
        self.agent.send_message(
            "The moderator has allowed you to speak. Start your message with a percent sign (%)"
        ).result(timeout=300)
        time.sleep(1)
        message_future = self.agent.get_latest_response()
        message = message_future.result(timeout=300)
        if message is None:
            raise Exception("Couldn't retrieve response from Claude for %s" % self.name)
        if message[0] != "%":
            self.agent.send_message(
                "Please start your message with a percent sign (%)"
            ).result(timeout=300)
            time.sleep(1)
            return self.get_allowance()
        self.cmd_wrapper("msg_team", message[1:])
