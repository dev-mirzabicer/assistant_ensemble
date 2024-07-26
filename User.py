class User:
    def __init__(self, name, introduction, preferences, assistant):
        self.name = name
        self.introduction = introduction
        self.preferences = preferences
        self.assistant = assistant
        self.waiting_for_response = False

    def get_message(self, message):
        print(f"Assistant: {message}")
        self.waiting_for_response = True

    def send_message(self, message):
        self.assistant.agent.send_message(f"{self.name} said: {message}").result(300)

    def introduce(self):
        self.assistant.agent.send_message(
            f"Let's first know the user. The user's self introduction is: {self.introduction}\n\nAnd the user's preferences for your style are: {self.preferences}.\n\n Again, please respond with `!OK` to allow the user to enter their first prompt."
        ).result(300)
