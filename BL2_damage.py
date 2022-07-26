"""Borderlands 2 Gun Damage Estimator

TkInter GUI.

Created on 7/6/2022    @author: aldon


Future enhancements
- Criticals
- Character skill buffs
- Badass buffs
- Class mod buffs
- Relic buffs
- Mfr buffs
- Weapon type buffs

"""
import sys
import os
import csv
import random
from math import ceil
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog as fd
import Pmw


def test():
    ent_name.delete(0, 'end')
    ent_name.insert(0, "Tactical something")
    
    ent_damage.delete(0, 'end')
    ent_damage.insert(0, "761")
    
    ent_pellets.delete(0, 'end')
    ent_pellets.insert(0, "1")
    
    ent_acc.delete(0, 'end')
    ent_acc.insert(0, "93.")
    
    ent_fr.delete(0, 'end')
    ent_fr.insert(0, "6.9")
    
    ent_rs.delete(0, 'end')
    ent_rs.insert(0, "1.5")
    
    ent_mag.delete(0, 'end')
    ent_mag.insert(0, "21")
    
    etype.set("Corrosive")
    etype_selected("Corrosive")
    
    ent_edmg.delete(0, "end")
    ent_edmg.insert(0, "245.1")
    
    ent_echa.delete(0, "end")
    ent_echa.insert(0, "14.4")
    
    ent_bps.delete(0, "end")
    ent_bps.insert(0, "2")
    

def reset_inputs():
    """
    Resets input cells to default values.

    Returns
    -------
    None.

    """
    ent_name.delete(0, 'end')
    ent_damage.delete(0, 'end')
    ent_damage.insert(0, '0')
    ent_pellets.delete(0, 'end')
    ent_pellets.insert(0, "1")
    ent_acc.delete(0, 'end')
    ent_acc.insert(0, '0')
    ent_fr.delete(0, 'end')
    ent_fr.insert(0, '0')
    ent_rs.delete(0, 'end')
    ent_rs.insert(0, '0')
    ent_mag.delete(0, 'end')
    ent_mag.insert(0, '0')
    etype.set("None")    
    ent_edmg.delete(0, "end")
    ent_edmg.insert(0, '0')
    ent_echa.delete(0, "end")
    ent_echa.insert(0, '0')
    mfr.set('tbd')
    ent_bps.delete(0, "end")
    ent_bps.insert(0, "1")

    
def elementals(elem_type):
    """
    Returns the elemental duration and factors for Target type. 

    Parameters
    ----------
    elem_type : string
        Type of elemental damage if any.

    Returns
    -------
    list of floats
        Damage factor for Flesh, Shield and Armor.

    """
    if elem_type == "None":
        return 0, [1, 1, .8]
    if elem_type == "Explosive":
        return 0, [1, .8, 1]
    elif elem_type == "Fire":
        return 5., [1.5, .75, .75]
    elif elem_type == "Shock":
        return 2., [1, 2, 1]
    if elem_type == "Corrosive":
        return 8., [.9, .75, 1.5] 
    elif elem_type == "Slag":
        return 8., [1, 1, 1]
    else:
        return 0, [1,1,1]

class Proc():
    """Models elemental damage from a sucessful hit over time"""
    
    def __init__(self, damage, duration):
        self.damage = damage
        self.timer = duration
    
    def step(self):
        self.timer -= 1  # reduce remaining time by one second
        if self.timer < 0:
            self.damage = 0


def etype_selected(etyp):
    if etyp == "Explosive":
        ent_edmg.delete(0, "end")
        ent_edmg.insert(0, "0")
        ent_edmg.config({"background": "gray"})
        ent_echa.config({"background": "gray"})
        ent_echa.delete(0, "end")
        ent_echa.insert(0, "100")
        ent_etype.configure(bg="yellow", fg="black")
    elif etyp=="Slag":
        ent_edmg.delete(0, "end")
        ent_edmg.insert(0, "0")
        ent_edmg.config({"background": "gray"})
        ent_echa.config({"background": "white"})
        ent_etype.configure(bg="purple", fg="white")
    elif etyp=="Fire":
        ent_etype.configure(bg="dark orange", fg="white")
        ent_edmg.config({"background": "white"})
        ent_echa.config({"background": "white"})
    elif etyp=="Corrosive":
        ent_etype.configure(bg="green", fg="white")
        ent_edmg.config({"background": "white"})
        ent_echa.config({"background": "white"})        
    elif etyp=="Shock":
        ent_etype.configure(bg="sky blue", fg="black")
        ent_edmg.config({"background": "white"})
        ent_echa.config({"background": "white"})        
    else:
        ent_etype.configure(bg="white", fg="black")
        ent_edmg.config({"background": "gray"})
        ent_echa.config({"background": "gray"})
        ent_edmg.delete(0, "end")
        ent_edmg.insert(0, "0")
        ent_echa.delete(0, "end")
        ent_echa.insert(0, "0")


def on_error(err_msg):
   messagebox.showerror('BL2 Gun Damage Error',
                           err_msg)


def calc_damage(ncycles=1000):
    
    # get current values from GUI
    try:
        dmg = int(ent_damage.get())
        dpel = int(ent_pellets.get())
        acc = float(ent_acc.get())
        mag = int(ent_mag.get())
        edps = float(ent_edmg.get())
        echa = float(ent_echa.get())
        fr = float(ent_fr.get())
        rs = float(ent_rs.get())
        bpsh = int(ent_bps.get())
        
    except:
        msg = sys.exc_info()[1]
        on_error("Input Error: Check for missing or non-numeric entries.\n\n" +
                 msg.args[0])
        return
        
    if bpsh <= 0:
        on_error("Ammo per shot must be > 0.")
        return
    
    if fr <= 0:
        on_error("Fire rate must be > 0.")
        return

    shots_mag = ceil(mag / bpsh)  # note 1 in readme.md    
    firing_time = shots_mag / fr  
    cycle_time = firing_time + rs
    
    # simulated firing cycle list (1 or 0 for ncycles * ticks/cycle)
    #   1 = firing
    tick = 1/3  # seconds
    pellets_tick = fr * dpel * tick * acc/100  # pellets per tick
    firing_ticks = round(firing_time / tick)
    firing_cycle = [1]*firing_ticks + [0]*round(rs/tick)
    simulation = firing_cycle * ncycles  
    
    # avg kinetic damage per sec for flesh, shock and armor
    k_dmg = [(fac * dmg * dpel * shots_mag * acc / 100)/cycle_time
             for fac in [1, 1, .8]] 
    
    etyp = etype.get()
    esec, dfactors = elementals(etyp)
    
    if etyp=="None":
        e_dmg = [0, 0, 0]
        
    elif etyp=="Explosive":
        e_dmg = k_dmg[:]
        
    elif etyp=="Slag": 
        dfac = 1 # all damage factors = 1 for slagged damage
        # basic kinetic damage per second while firing
        k_raw = dmg * dpel * fr *  acc / 100
        enet = 0
        procs = []  # Proc list
        for i in range(len(simulation)):
            if simulation[i]:
                # probability of spawning a new Proc
                prob = 1 - (1-echa/100)**pellets_tick
                if random.random() < prob:
                    procs.append(Proc(k_raw * dfac * tick, esec / tick))
    
            slag_dmg = 0
            # if any of the current Procs are active set slag_dmg to p.damage
            for p in procs:
                if simulation[i] and p.damage > 0:
                    slag_dmg = p.damage
                p.step()
                # cleanup dead Procs
                if p.damage == 0:
                    procs.remove(p)
                
            enet += slag_dmg
            
        e_dmg = [(enet / ncycles)/cycle_time]
        e_dmg = e_dmg * 3
        
        
    else:
        enet = 0   # initialize net damage for the simulation period   
        dfac = 1.  # I will multiply by target damage factors later
        procs = []  # list of active Procs
        for i in range(len(simulation)):
            if simulation[i]:
                prob = 1 - (1-echa/100)**pellets_tick
                if random.random() < prob:
                    procs.append(Proc(edps * dfac * tick, esec / tick))

            # accumulate damage for all active Procs        
            dmg = 0        
            for p in procs:
                dmg += p.damage
                p.step()
                if p.damage == 0:
                    procs.remove(p)
                
            enet += dmg

        # average elemental damage per sec to flesh, shield and armor:    
        e_dmg = [enet * f / ncycles / cycle_time for f in dfactors]
                
    # combine kinetic and elemental damage
    damage_per_sec = [(k_dmg[i] + e_dmg[i]) for i in range(len(k_dmg))]
    
    avg_dps = sum(damage_per_sec)/ len(damage_per_sec)
    
    out_flesh["text"] = f"{damage_per_sec[0]:.1f}"
    out_shields["text"] = f"{damage_per_sec[1]:.1f}"
    out_armor["text"] = f"{damage_per_sec[2]:.1f}"
    out_avg["text"] = f"{avg_dps:.1f}"


def save_gun():
    """
    Append current inputs and results to comparison window.
    """
    compare.deiconify()
    gun_comp.insert('', tk.END, text='',
                    values=(ent_name.get(),
                            wtype.get(),
                            ent_damage.get() + ' X ' + ent_pellets.get(), 
                            ent_acc.get(),
                            ent_fr.get(),
                            ent_rs.get(),
                            ent_mag.get(),
                            etype.get(),
                            ent_edmg.get(),
                            ent_echa.get(),
                            ent_bps.get(),
                            mfr.get(),
                            out_flesh.cget("text"), 
                            out_shields.cget("text"),
                            out_armor.cget("text"),
                            out_avg.cget("text")
                            )
                    )


def clear_compare():
    """Clears all rows in compare table after user verifies their intent"""
    
    msg_box = messagebox.askquestion ('Delete Data',
                                         'Are you sure you want to clear the data?',
                                         icon = 'warning')
    if msg_box == 'yes':
        for row in gun_comp.get_children():
            gun_comp.delete(row)
        return
    else:
        return

    
def delete_row():
    """Delete selected row."""
    selected_item = gun_comp.selection()[0]
    gun_comp.delete(selected_item)


def sort_damage():
    """
    Sort comparison table by average gun damage in descending order.
    """
    tree = gun_comp
    column = 'dps_avg'    
    rows = [(tree.set(item, column), item) for item in tree.get_children('')]
    rows.sort(reverse=True)

    # rearrange items in sorted positions
    for index, (values, item) in enumerate(rows):
        tree.move(item, '', index)


def export():
    """export comparison table values to a csv file"""
    
    
    homeDir = os.path.expanduser("~")
    
    file = fd.asksaveasfile(mode='w', initialdir=homeDir+"/Documents/",
                                 defaultextension='.csv')
    if file is None:
        return
    
    with open(file.name, mode='w', newline='') as gun_file:
        gun_writer = csv.writer(gun_file, delimiter=',')
        
        gun_writer.writerow(['gun_name', 'gun_type', 'dmg_basic', 'accuracy',
                            'fire_rate', 'reload', 'magsize', 
                            'elem_type', 'elem_dps', 'elem_chance',
                            'bpshot', 'mfr', 
                            'dps_flesh', 'dps_shock', 'dps_armor', 'dps_avg'])
        
        saved_guns = gun_comp.get_children()
        for gun in saved_guns:
            gun_writer.writerow(gun_comp.item(gun)['values'])

    return    


def import_csv():
    """import saved gun comparison data."""
    
    homeDir = os.path.expanduser("~")  
    
    # have user select desired csv file
    file_name = fd.askopenfilename(title='Open a csv file',
        initialdir= homeDir + '\\Documents\\', 
        filetypes=[('csv files', '*.csv')])
    
    with open(file_name, mode='r', newline='') as gun_file:
        # read file one line at a time
        # for each data row, insert a row into compare table with those values
        row_reader = csv.reader(gun_file, delimiter=',')
        line_count = 0
        for row in row_reader:
            if line_count == 0:
                line_count += 1
                continue
            else:
                gun_comp.insert('', tk.END, text='',
                                values=row )
                line_count += 1

    
#%% TkInter GUI components
# Set-up the main window

window = tk.Tk()
window.title("BL2 Gun Damage")
window.resizable(width=False, height=False)

#%% Inputs
frm_entry = tk.Frame(window) # instantiate the entry form object
frm_output = tk.Frame(window)  # the results frame
frm_controls = tk.Frame(window)   # for controls i.e. buttons
"""Create the entry frames with Entry widgets and labels and
Layout the Entries and Labels in frm_entry
using the .grid() geometry manager
"""
# gun name
lbl_name = tk.Label(frm_entry, text="Name", anchor='w')
ent_name = tk.Entry(frm_entry)
lbl_name.grid(row=0, column=0, sticky="w")
ent_name.grid(row=0, column=1, columnspan=3, sticky="nesw")

# projectile damage and n pellets per round (e.g. shotties)
lbl_damage = tk.Label(frm_entry, text="Damage", anchor='w')
lbl_damage.grid(row=1, column=0, sticky='w')
ent_damage = tk.Entry(frm_entry,  justify='center')
ent_damage.grid(row=1, column=1, sticky='nesw')
lbl_x = tk.Label(frm_entry, text=" X ")
lbl_x.grid(row=1, column=2)
ent_pellets = tk.Entry(frm_entry, width=4, justify='center')
ent_pellets.grid(row=1, column=3)

# Accuracy
lbl_acc = tk.Label(frm_entry, text="Accuracy %")
ent_acc = tk.Entry(frm_entry,  justify='center')
lbl_acc.grid(row=2, column=0, sticky='w')
ent_acc.grid(row=2, column=1, sticky='nesw')
# fire rate
lbl_fr = tk.Label(frm_entry, text="Fire Rate")
ent_fr = tk.Entry(frm_entry,  justify='center')
lbl_fr.grid(row=3, column=0, sticky='w')
ent_fr.grid(row=3, column=1, sticky='nesw')
# reload speed
lbl_rs = tk.Label(frm_entry, text="Reload Speed")
ent_rs = tk.Entry(frm_entry,  justify='center')
lbl_rs.grid(row=4, column=0, sticky='w')
ent_rs.grid(row=4, column=1, sticky='nesw')
# magazine size
lbl_mag = tk.Label(frm_entry, text="Magazine Size")
ent_mag = tk.Entry(frm_entry,  justify='center')
lbl_mag.grid(row=5, column=0, sticky='w')
ent_mag.grid(row=5, column=1, sticky='nesw')

# Elemental type drop down
lbl_etype = tk.Label(frm_entry, text="Elemental Type")
etype = tk.StringVar()
etype.set("None")
ent_etype = tk.OptionMenu(frm_entry, etype, "None", "Corrosive",
                          "Explosive", "Fire", "Shock", "Slag",
                          command=etype_selected)
# ent_etype.config(width=7, bg="GREEN", fg="WHITE")
lbl_etype.grid(row=6, column=0, sticky='w')
ent_etype.grid(row=6, column=1, sticky='nesw') 

# Elemental damage
lbl_edmg = tk.Label(frm_entry, text="Elem Dmg/sec")
ent_edmg = tk.Entry(frm_entry,  justify='center')
lbl_edmg.grid(row=7, column=0, sticky='w')
ent_edmg.grid(row=7, column=1, sticky='nesw')

# Elemental Chance
lbl_echa = tk.Label(frm_entry, text="Elem Chance %")
ent_echa = tk.Entry(frm_entry,  justify='center')
lbl_echa.grid(row=8, column=0, sticky='w')
ent_echa.grid(row=8, column=1, sticky='nesw')

# Ammo per shot
lbl_bps = tk.Label(frm_entry, text="Ammo per Shot")
ent_bps = tk.Entry(frm_entry, justify='center')
lbl_bps.grid(row=9, column=0, sticky='w')
ent_bps.grid(row=9, column=1, sticky='nesw')

# Manufacturer
lbl_mfr = tk.Label(frm_entry, text="Manufacturer")
lbl_mfr.grid(row=10, column=0, sticky='w')
mfr = tk.StringVar()
mfr.set("Torque")
ent_mfr = tk.OptionMenu(frm_entry, mfr, "Dahl", "Hyperion", "Jakobs",  "Maliwan",
                        "Torque", "Tediore", "Vladof", "Other")  
# ent_mfr.config(width=7, bg="BROWN", fg="WHITE")
ent_mfr.grid(row=10, column=1, sticky='ew')

# Weapon Type
lbl_type = tk.Label(frm_entry, text="Type")
lbl_type.grid(row=11, column=0, sticky='w')
wtype = tk.StringVar()
wtype.set("Pistol")
ent_type = tk.OptionMenu(frm_entry, wtype, "Assault", "Launcher",  "Pistol",
                        "Sniper", "Shotgun", "Submachine")
# ent_type.config(width=7, bg="BLUE", fg="WHITE")
ent_type.grid(row=11, column=1, sticky='nesw')


#%% Controls
# Populate input frames with test values. 
btn_test = tk.Button(frm_controls, text="Test", command=test)
btn_test.grid(row=0, column=0, sticky='w', pady=5)
# reset inputs to defaults
btn_reset = tk.Button(frm_controls, text="Reset", command=reset_inputs)
btn_reset.grid(row=0, column=1, sticky='w', pady=5)
# compute damage
btn_calc = tk.Button(frm_controls,
    text="Calculate",
    command=calc_damage)
btn_calc.config(bg="green", fg="WHITE")
btn_calc.grid(row=0, column=2, pady=5, sticky='ew')

btn_save = tk.Button(frm_controls,
                       text="Save",
                       command=save_gun)
btn_save.grid(row=0, column=3, pady=5, sticky='ew')

#%% Results
lbl_flesh = tk.Label(frm_output, text="Flesh")
lbl_flesh.grid(row=0, column=0, sticky='w')
lbl_shields = tk.Label(frm_output, text="Shields")
lbl_shields.grid(row=1, column=0, sticky='w')
lbl_armor = tk.Label(frm_output, text="Armor")
lbl_armor.grid(row=2, column=0, sticky='w')

lbl_avg = tk.Label(frm_output, text="Average")
lbl_avg.grid(row=3, column=0, sticky='w')

out_flesh = tk.Label(frm_output, justify='center',
                     width=10, borderwidth=1, relief="solid")
out_flesh.grid(row=0, column=1, sticky='ew')
out_shields = tk.Label(frm_output, justify='center',
                     width=10, borderwidth=1, relief="solid")
out_shields.grid(row=1, column=1, sticky='ew')
out_armor = tk.Label(frm_output, justify='center',
                     width=10, borderwidth=1, relief="solid")
out_armor.grid(row=2, column=1, sticky='ew')

out_avg = tk.Label(frm_output, justify='center',
                     width=10, borderwidth=1, relief="solid")
out_avg.grid(row=3, column=1, sticky='ew')

#%% add frm_entry, frm_controls and frm_output to the master window
frm_entry.grid(row=0, column=0, padx=15, pady=15)
frm_controls.grid(row=1, column=0, padx=15, pady=0)
frm_output.grid(row=2, column=0, padx=15, pady=15)

#%% Child window used for comparing guns

compare = tk.Toplevel(window)
compare.geometry('1350x400')
compare.resizable(width=True, height=True)
compare.title("BL2 Gun Damage Comparison")
# row 0
frame1 = tk.Frame(compare)
l1 = tk.Label(frame1, text=' ')
l1.grid(column=1, row=0)
l8 = tk.Label(frame1, text="Elemental", justify='center',
              bg="yellow")
l8.grid(column=8, row=0, sticky='ew')
l9 = tk.Label(frame1, text=' ')
l9.grid(column=9, row=0)
l10 = tk.Label(frame1, text="Damage per Second", justify='right',
               bg='sky blue')
l10.grid(column=10, row=0, sticky='ew')
frame1.columnconfigure(1, {'minsize': 600})
frame1.columnconfigure(8, {'minsize': 250})
frame1.columnconfigure(9, {'minsize': 160})
frame1.columnconfigure(10, {'minsize': 320})
frame1.grid(row=0, column=0, sticky='ew')
# row1
gun_comp = ttk.Treeview(compare)
gun_comp['columns'] = ('gun_name', 'gun_type', 'dmg_basic', 'accuracy',
                       'fire_rate', 'reload', 'magsize', 
                       'elem_type', 'elem_dps', 'elem_chance',
                       'bpshot', 'mfr', 
                       'dps_flesh', 'dps_shock', 'dps_armor', 'dps_avg')

gun_comp.column("#0", width=0,  stretch=False)
gun_comp.column("gun_name",anchor='center', width=120)
gun_comp.column("gun_type",anchor='center', width=80)
gun_comp.column("dmg_basic",anchor='center', width=80)
gun_comp.column("accuracy",anchor='center', width=80)
gun_comp.column("fire_rate",anchor='center', width=80)
gun_comp.column("reload",anchor='center', width=80)
gun_comp.column("magsize",anchor='center', width=80)
gun_comp.column("elem_type",anchor='center', width=80)
gun_comp.column("elem_dps",anchor='center', width=80)
gun_comp.column("elem_chance",anchor='center', width=90)
gun_comp.column("bpshot",anchor='center', width=80)
gun_comp.column("mfr",anchor='center', width=80)
gun_comp.column("dps_flesh",anchor='center', width=80)
gun_comp.column("dps_shock",anchor='center', width=80)
gun_comp.column("dps_armor",anchor='center', width=80)
gun_comp.column("dps_avg",anchor='center', width=80)

gun_comp.heading("#0",text="",anchor='center')
gun_comp.heading("gun_name",text="Name",anchor='center')
gun_comp.heading("gun_type",text="Type",anchor='center')
gun_comp.heading("dmg_basic",text="Damage",anchor='center')
gun_comp.heading("accuracy",text="Accuracy %",anchor='center')
gun_comp.heading("fire_rate",text="Fire rate",anchor='center')
gun_comp.heading("reload",text="Reload sec",anchor='center')
gun_comp.heading("magsize",text="Mag size",anchor='center')
gun_comp.heading("elem_type",text="Elem Type",anchor='center')
gun_comp.heading("elem_dps",text="Elem DPS",anchor='center')
gun_comp.heading("elem_chance",text="Elem Chance %",anchor='center')
gun_comp.heading("bpshot",text="Ammo/shot",anchor='center')
gun_comp.heading("mfr",text="Manufacturer",anchor='center')
gun_comp.heading("dps_flesh",text="Flesh",anchor='center')
gun_comp.heading("dps_shock",text="Shields",anchor='center')
gun_comp.heading("dps_armor",text="Armor",anchor='center')
gun_comp.heading("dps_avg",text="Average",anchor='center')

gun_comp.grid(row=1, column=0, sticky='ew')

# row 2
frame2 = tk.Frame(compare)

btn_import = tk.Button(frame2, text="  Import   ",  command=import_csv)
btn_import.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
btn_import.config(bg="sky blue", fg="black")

btn_export = tk.Button(frame2, text="   Export   ", command=export)
btn_export.grid(row=1, column=1, sticky='ew', padx=10, pady=5)
btn_export.config(bg="sky blue", fg="black")

btn_sort = tk.Button(frame2, text="   Sort   ", command=sort_damage)
btn_sort.grid(row=1, column=2, sticky='ew', padx=10, pady=5)
btn_sort.config(bg="sky blue", fg="black")

btn_del = tk.Button(frame2, text="   Delete Selected   ", command=delete_row)
btn_del.grid(row=1, column=3, sticky='ew', padx=10, pady=5)
btn_del.config(bg="tomato2", fg="black")

btn_clear = tk.Button(frame2, text="   Clear All   ", command=clear_compare)
btn_clear.grid(row=1, column=4, sticky='ew', padx=10, pady=5)
btn_clear.config(bg="tomato2", fg="black")

#Create and bind tooltips
tip_del = Pmw.Balloon(compare)
tip_del.bind(btn_del, "Delete selected row")
tip_exp = Pmw.Balloon(compare)
tip_exp.bind(btn_export, "Export to csv file")
tip_imp = Pmw.Balloon(compare)
tip_imp.bind(btn_import, "Import from csv file")
tip_clr = Pmw.Balloon(compare)
tip_clr.bind(btn_clear, "Clear all items from table")
tip_srt = Pmw.Balloon(compare)
tip_srt.bind(btn_sort, "Sort items by average damage (descending)")

frame2.grid(row=2)


#%% Initialize and run
# insert default values
ent_pellets.insert(0, "1")
ent_bps.insert(0, "1")
# hide compare window
compare.withdraw()

# Run the application
window.mainloop()