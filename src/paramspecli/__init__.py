"""Type-safe facade for the venerable argparse"""

__version__ = "0.2.1"


from .args import argument as argument
from .cli import Action as Action
from .cli import CallableGroup as CallableGroup
from .cli import Command as Command
from .cli import Config as Config
from .cli import Group as Group
from .cli import Handler as Handler
from .cli import Route as Route
from .cli import help_action as help_action
from .cli import version_action as version_action
from .conv import PathConv as PathConv
from .fake import Const as Const
from .fake import Context as Context
from .fake import deprecated as deprecated
from .fake import required as required
from .fake import t as t
from .flags import count as count
from .flags import flag as flag
from .flags import repeated_flag as repeated_flag
from .flags import switch as switch
from .opts import option as option
from .opts import repeated_option as repeated_option
