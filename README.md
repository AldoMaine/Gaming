# Borderland 2 Gun Damage Calculator App

...a work in progress....  

## Introduction
A basic Python app using the TkInter library to compute the damage per second (DPS) for guns in Borderlands 2. While I agree that field testing a gun is the best way to see if it works well for you, sometimes you want a quick way to compare several guns. 

## How to use. 
* Download 'BL2 Damage Calculator.exe' to your PC. 
* Double click 'BL2 Damage Calculator.exe' to start. (takes 15-20 seconds to start)  
* Enter gun data from BL2 weapon card.  UI is designed to follow order of parameters seen on BL2 weapon cards.  
* Click  'Calculate' to view predicted damage for each target type in UI.  
* Click 'Save' to add this gun and it's damage results to a comparison table.  The comparison table will be shown in a new window.   
* Using the main window, analyze and save other guns to the table as desired.   
* The following functions are available in the compare window:
 > * 'Export' the data to a csv file.  
 > * 'Import' previously exported gun data from a csv file.  
 > * 'Sort' guns by average damage (descending order)  
 > * 'Clear' removes alls guns currently displayed in comparison window.   
 > * 'Delete Selected' deletes the currently selected gun. (click on row to select)    	

## Damage Equations
I found a lot of content on various sites dealing with this subject.  Unclear if any of it is vetted by game devs.  There is a flash page called Gearcalc that is widely cited  but flash is considered so toxic now that no browser will run it.   What follows is my understanding gleaned from what I found.  I was able to verify some of the damage estimates in-game at Marcus's Gun Shop in Sanctuary.  Once you do the mission where he introduces you to the shooting range, you can test most guns on the poor schmuck tied to the target.  When I first tried this, I noticed the numbers flying off the target were higher than I predicted.  This was because I haven't factored in the damage improvements from class mods, relics, and so on.  In my attempt to keep the calculation simple and understandable I chose to leave those effects out for now.  
### Weapon Cards  
Here is a typical weapon card for a gun in BL2.   
![image](https://user-images.githubusercontent.com/11415077/179798465-1c24e87d-68f0-44ec-9eed-6bbd22dfd3b9.png)  
I designed the GUI for my damage app to follow the flow of the information on the weapon cards. 

### Basic Damage  
Also called kinetic or projectile damage, it is the damage done purely by the bullets or pellets that hit the target.  For most guns a single "Damage" number is given.  A succcessful hit will do about this much damage to the target.  For some guns, especially shotguns, a second number is shown next to the damage, for example; "653 x 13".  The second number is the number of pellets.  For the example given, each "shot" fires 13 pellets, each of which does 653 damage. This impressive potential is rarely achieved since shotguns are not very accurate.   Some guns shoot multiple rounds per shot.  This is shown on the weapon card as "Consumes X ammo per shot".  This extra ammo you're shooting doesn't change the damage per shot, it's already factored in.  What it does is increase the rate of ammo usage and means you will burn through a magazine quicker.   
#### Definitions:  
$dmg =$ damage from a single bullet or pellet.   
$dpel =$ number of pellets per shot, shown as 'x dpel' on the weapon card.
$acc =$ accuracy %.  A well aimed shot should hit the target this percent of the time.  Affected by distance to target and weapon zoom.  
$fr =$ fire rate.  Maximum shots per second possible.  Semi-automatic guns (e.g. most pistols) require a trigger pull for each shot.  If you're slow on the trigger, you might not achieve the stated fire rate.   
$rs =$ reload speed.  The time in seconds to reload the gun.   
$mag =$ magazine size.  The number of rounds in a full magazine.  
$bpsh =$ ammo per shot.  
$fac =$ target damage factor.  For kinetic damage, the factors are 1.0 for flesh and shields and 0.8 for armor.  
  
The time it takes to empty a full magazine:    $$\Large t_{firing}=\frac{mag}{fr \cdot  bpsh}$$  
Average kinetic damage per second over a full firing+reload cycle:  
$$\Large DPS_{kinetic} = \frac{fac \cdot dmg \cdot dpel \cdot \frac{mag}{bpsh} \cdot \frac{acc}{100}}{rs+t_{firing} }$$

### Elemental Damage
In BL2 there are several types of "elemental" damage that some guns can inflict; Incendiary(Fire), Shock, Corrosive, Slag and Explosive.  The first 3 behave similarly except for their effect on the target and how long they last.  Slag doesn't inflict any damage by itself but causes other damage types to inflict double damage. Explosive weapons also can do double damage but the explosive part is splash damage and it happens instantly.   
**Damage Factors vs. Target Type**
| Target | Incendiary | Shock | Corrosive |  
|--------|------------|-------|-----------|  
| Flesh  |    1.50    | 1.00  |   0.90    |  
| Shield |    0.75    | 2.00  |   0.75    |  
| Armor  |    0.75    | 1.00  |   1.50    |  

The effectiveness of elementals depends on the type of target.  Flesh targets are strongly affected by incendiary effects but not so much by corrosive effect. 

#### Procs (Programmed Random Occurences)
Incendiary, Shock, Corrosive and Slag elemental effects happen based on random chance.  This is shown on the weapon card as "Corrode chance 37.5%" for example. This means that for every bullet or pellet that hits the target there is an x% chance that an elemental effect will occur.  We call these "procs".  Procs last for varying amounts of time based on the elemental type.  Multiple procs can be in effect concurrently.  You can see this effect if you try your elemental weapon at Marcus's range.  Keep firing and watch the damage numbers flying off the unfortunate target multiply.

In the spreadsheet caclulators I've seen elemental damage chance is simply applied as a factor.  This implies that every bullet does elemental damage but at a reduced rate based on the chance percentage.  It does not allow for concurrent procs or their timelines.  To better simulate elemental effects and their procs I took a different approach.  
* I simulate 1000 firing cycles. A firing cycle consists of the time it takes to fire all the shots in the magazine plus the reload time.  I do 1000 cycles becasue of the random nature of the procs.  The first cycle might trigger no procs.  The 13th might trigger several.  If I do enough, I can average it out. 
* Each second is divided into ticks because that is how BL2 handles time internally.  A tick in BL2 is 1/3 of a second. So 10 seconds equals 30 ticks.
* The simulation is just a long list of 1's and zeros.  A 1 means the gun is firing during that tick and a zero means it isn't.
* The code steps through each tick in the simulation list.
* At each tick where firing is occuring it generates a random number and compares that the elemental chance. Think of this as rolling a many sided die. If the number you get is equal or less than the elemental chance then a proc is triggered.  For example, if the random number is 0.32 or 32% and the elemental chance is 45.2% then a proc is triggered.  Remember that multiple procs can be active at the same time.  The damage per tick assigned to the proc is 1/3 the elemental damage per second shown on the weapon card.  
(TODO show the picture in an endnote?) 
* At each tick the program sums up the elemental damage for all the active procs and reduces the time remaining on all of them by one tick. When a proc timer runs out, it is retired. 
* The damage for each tick is accumulated over the entire simulation.  

$enet =$ accumulated elemental damage for 1000 cycles.   
$fac =$ target damage factor from table above.  
$ncycles =$ number of simulation cycles.  
$cycle time =$ firing+reload cycle time.  

Average elemental damage per second:
$$\Large DPS_{elemental} = \frac{enet \cdot fac}{ncycles \cdot cycletime}$$

#### Splash    
All elemental effects have a "splash" characteristic.  This means that a poorly aimed shot might still damage the target.  It also means that when a proc triggers on a successful hit, nearby enemies might also be affected by the same elemental damage. 

#### Incendiary Damage
Highly effective against fleshy targets. 5 second duration.
  
#### Shock Damage
Highly effective against shields. 2 second duration. 

#### Corrosive damage
Highly effective against armored targets. 8 second duration. 

#### Slag damage
Doubles other damage types once a target is slagged.  8 second duration.  

#### Explosive damage
Doubles kinetic damage.  Can cause splash explosive damage nearby targets. 

### Total DPS
The total DPS is simply:
$$\Large DPS=DPS_{kinetic}+DPS_{elemental}$$
The calculations above are repeated for each target type (flesh, shields and armor) and the results are shown in the main window.  An average of these 3 DPS numbers is also calculated and shown.  
	
## What isn’t included (yet)  
* Criticals
* Buffs for character, relic, class mods, etc…

## Supported systems
* MS Windows  

