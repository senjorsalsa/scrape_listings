from tkinter import *
from scraper import scrape_main

window = Tk()
window.title("Hitta lägenheter")
window.config(padx=20, pady=20)
window.geometry("280x200")

def button_clicked():
    scrape_main(var1, var2, var3, var4)

var1 = IntVar()
var2 = IntVar()
var3 = IntVar()
var4 = IntVar()

blocket_check = Checkbutton(text="Blocket", variable=var1, onvalue=1, offvalue=0)
blocket_check.grid(row=0, column=0, sticky="w")

riks_check = Checkbutton(text="Riksbyggen", variable=var2, onvalue=1, offvalue=0)
riks_check.grid(row=1, column=0, sticky="w")

heim_check = Checkbutton(text="Heimstaden", variable=var3, onvalue=1, offvalue=0)
heim_check.grid(row=2, column=0, sticky="w")

boplats_check = Checkbutton(text="Boplats Syd", variable=var4, onvalue=1, offvalue=0)
boplats_check.grid(row=3, column=0, sticky="w")

submit_button = Button(text="Hämta lägenheter", command=button_clicked)
submit_button.grid(row=5, column=0, pady=10)

window.mainloop()
