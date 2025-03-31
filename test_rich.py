from rich import print
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.padding import Padding
from rich.table import Table
from rich import box
import time
from rich.live import Live
from rich.progress import Progress



console = Console()

layout = Layout()
titre = Text("JEU DU PENDU", justify="center")
titre.stylize( "salmon1", 0, 12 )

classement = Table(box= box.DOUBLE, title="Classement", style =  "salmon1")
classement.header_style = "light_goldenrod2"
classement.title_style = "light_goldenrod2"
classement.add_column("Joueur", justify="right", style="light_goldenrod2", no_wrap=True, ratio= 8, min_width=20)
classement.add_column("Score", justify="right", style="light_goldenrod2", min_width=20)



layout.split_column(
    Layout(name="upper"),
    Layout(name="lower")
)


layout["lower"].split_row(
    Layout(name="pendu"),
    Layout(name="right"),
)


layout["upper"].split_column(
    Layout(Panel(titre, style= "salmon1", expand=True)),
    Layout(name = "mot a trouver")
 )



layout["right"].split_row(
    Layout(name = "lettres"),
    Layout(name ="full right")
)
layout["full right"].split_column(
    Layout(classement, name = "classement"),
    Layout(name ="time")
)
layout["lower"].size = None
layout["lower"].ratio = 3
layout["classement"].size = None
layout["classement"].ratio = 15

def countdown_timer(seconds):
    with Live(layout, refresh_per_second=1):
        for remaining in range(seconds, -1, -1):
            timer_text = Text(f"Temps restant : {remaining}s", justify="center", style="medium_turquoise" )
            layout["time"].size = None
            layout["time"].ratio =2
            layout["time"].update(Panel(timer_text, style="salmon1"))
            time.sleep(1)

countdown_timer(3)  
with Live(layout, refresh_per_second=4): 
    for row in range(12):
        time.sleep(0.2) 
        score = row*20
        classement.add_row(f"Joueur{row}", f"{score}")

  
console.print(layout)
