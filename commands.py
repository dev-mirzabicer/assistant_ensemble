from Assistant import Assistant
from Team import Team
import os
from User import User


def command_wrapper(assistant, team):
    def command(cmd, *args):
        if cmd in cmds:
            return cmds[cmd](assistant, team, *args)
        return "Command not found."

    return command


def whisper(sender, team, message, receiver_name):
    # receiver.get_whisper(sender.name, message)
    team.whisper(sender, message, receiver_name)
    return "Message sent."


def msg_team(sender, team, message):
    team.message(sender, message)
    return "Message sent."


def raise_hand(agent, team):
    team.moderator.agent.send_message(f"{agent.name} raised their hand.").result()
    return "Hand raised."


def allowspeak(moder, team, agent):
    # agent.get_allowance()
    # return f"Allowed {agent.name} to speak."
    res = team.let_allowance(agent)
    if res is not None:
        return res


def list(agent, team):
    return os.listdir(f"./team_folders/{team.session_id}/filebase")


def delete(agent, team, file_name):
    os.remove(f"./team_folders/{team.session_id}/filebase/{file_name}")
    return f"Deleted {file_name}."


def write(agent, team, file, content):
    with open(f"./team_folders/{team.session_id}/filebase/{file}", "w") as f:
        f.write(content)
    return f"Written to {file}."


def read(agent, team, file_name):
    with open(f"./team_folders/{team.session_id}/filebase/{file_name}", "r") as f:
        return f.read()


def preview(agent, team, file_name, lines):
    with open(f"./team_folders/{team.session_id}/filebase/{file_name}", "r") as f:
        return f.read().split("\n")[: int(str(lines).strip())]


def run(agent, team, cmd):
    os.system(f"cd team_folders/{team.session_id}/filebase && {cmd}")
    return "Command executed."


def msg_user(agent, team, message, user):
    # user.get_message(message)
    # return "Message sent."
    res = team.message_user(agent, message, user)
    if res is not None:
        return res


def note(agent, team, note):
    with open(f"./team_folders/{team.session_id}/notes.txt", "a") as f:
        f.write(note + "\n")
    return "Note added."


def permanent_note(agent, team, note):
    with open(f"permanent_notes.txt", "a") as f:
        f.write(note + "\n")
    return "Permanent note added."


# other commands, also todo

# Important note: the command functions return values are directly given to agents as a response. design the return values accordingly.

cmds = {
    "!whisper": whisper,
    "!team": msg_team,
    "!raisehand": raise_hand,
    "!allowspeak": allowspeak,
    "!list": list,
    "!delete": delete,
    "!write": write,
    "!read": read,
    "!preview": preview,
    "!run": run,
    "!user": msg_user,
    "!note": note,
    "!permanentnote": permanent_note,
}
