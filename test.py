import textwrap
from time import sleep
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich.table import Column
from rich.bar import Bar
p = Progress(
    SpinnerColumn("dots3"),
    TextColumn("Liczba stron: {task.fields[test]}"),
    BarColumn(pulse_style="bar.pulse"),
    TextColumn("{task.fields[name]}",justify='right'),
)

def sh(s:str, width:int=20, from_end:int=5):
    trim = '…'
    if len(s)>width:
        return s[:width-len(trim)-from_end]+trim+s[-from_end:]
    return s

p.start()
name = "hej"
pid = p.add_task("Joe", total=None, test=12, name=name)
while True:
    name += "a"
    p.update(pid, name=sh(name))
    sleep(0.15)
