import logging
from rich.logging import RichHandler
import rich
from rich.pretty import pprint as rich_pprint
from importlib import import_module

class ModuleLogging:
    def __init__(self, name) -> None:
        self.log = logging.getLogger(name)
        self.log.addHandler(logging.NullHandler())
        self.console = None
    def pprint(self, obj, **kwargs):
        if self.console is None: return
        rich_pprint(obj,**kwargs)
    def debug_on(self, console=None):
        if console is None:
            console = rich.get_console()
        self.console = console
        self.log.addHandler(self.debug_handler())
        self.log.setLevel(logging.DEBUG)
    def debug_handler(self):
        return RichHandler(
            rich_tracebacks=True,
            console=self.console,
            show_level=False,
            show_time=False,
            show_path=False
        )
    def init(self):
        return self.log, self.pprint

def debug_on(modules,console=rich.get_console()):
    for module_name in modules:
        import_module(module_name).module_log.debug_on(console)