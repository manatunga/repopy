"""
Registry and main entrypoint of all repopy commands.
"""

from repopy.commands.clean import CleanCommand
from repopy.commands.clone import CloneCommand
from repopy.commands.info import InfoCommand
from repopy.commands.init import InitCommand
from repopy.commands.link import LinkCommand

_all_commands = [
    CleanCommand(),
    CloneCommand(),
    InfoCommand(),
    InitCommand(),
    LinkCommand(),
]

COMMANDS = {cmd.name: cmd for cmd in _all_commands}
