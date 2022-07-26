# Borderland 2 Gun Damage Calculator App

## Introduction
A basic Python app using the TkInter library to compute the damage per second (DPS) for guns in Borderlands 2. While I agree that field testing a gun is the best way to see if it works well for you, sometimes you want a quick way to compare several guns. 

## How to use. 
* Download 'BL2 Damage Calculator.exe' to your PC. 
* Double click 'BL2 Damage Calculator.exe' to start. (takes 15-20 seconds to start)  
* Enter gun data from BL2 weapon card.  UI is designed to follow order of parameters seen on BL2 weapon cards.  
* Click  'Calculate' to view predicted damage for each target type in UI.  (See 'Total DPS' below).
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
Also called kinetic or projectile damage, it is the damage done purely by the bullets or pellets that hit the target.  For most guns a single "Damage" number is given.  A succcessful hit will do about this much damage to the target.  For some guns, especially shotguns, a second number is shown next to the damage, for example; "653 x 13".  The second number is the number of pellets (see Burst Mode below).  For the example given, each "shot" fires 13 pellets, each of which does 653 damage. This impressive potential is rarely achieved since shotguns are not very accurate.   Some guns shoot multiple rounds per shot.  This is shown on the weapon card as "Consumes X ammo per shot".  This extra ammo you're shooting doesn't change the damage per shot, it's already factored in.  What it does is increase the rate of ammo usage and means you will burn through a magazine quicker.  

#### Accuracy and Spread
Accuracy is directly related to spread which is explained in detail [here](https://borderlands.fandom.com/wiki/Accuracy).  A perfectly aimed shot will randomly deviate from the perfect path within a cone defined by the spread angle.  As the linked article explains, there is a lot more to accuracy and spread but a simplified relationship between accuracy and spread is given by $spread = (100 − accuracy)/12$. A shotgun with an accuracy of 30% has a spread of roughly $5.8^{\circ}$.  If you are 10 feet away from your target this equals an aperture (far left to far right of cone at the target) of only 1 foot.  If you are 100 feet away the aperture increases to 10 feet.  The takeaway: if you're firing a low accuracy weapon, you want to be close to your target.  
The app uses accuracy as more of an effectiveness factor to reduce the theoretical damage done if all pellets hit the target.  It's conservative and if you're choosing the right gun for the job, you're probably getting more damage than the app indicates.  However, the goal is to *compare* guns. A shotgun with high accuracy will do the same damage to the target from farther away that a lower accuracy shottie.  That's better.  


#### Burst Mode
Some weapons fire multiple bullets per shot in a similar way to shotguns that have multiple pellets per shot.  This is shown the same way on the weapon card, e.g. "324 x 2".  This is typically accompanied by "Consumes 2 ammo per shot". The damage calculations are the same as for a shotgun.   
Another type of burst mode is a weapon card that says "Burst fire while zoomed".   This will probably improve your fire rate while zoomed compared to pulling the trigger once per shot.  Unfortunately the card does not say how many rounds per burst, etc. so the app does not try to factor this in. 

#### Definitions  
$dmg =$ damage from a single bullet or pellet.   
$dpel =$ number of pellets per shot, shown as 'x dpel' on the weapon card.
$acc =$ accuracy %.  A well aimed shot should hit the target this percent of the time.  Affected by distance to target and weapon zoom.  
$fr =$ fire rate.  Maximum shots per second possible.  Semi-automatic guns (e.g. most pistols) require a trigger pull for each shot.  If you're slow on the trigger, you might not achieve the stated fire rate.   
$rs =$ reload speed.  The time in seconds to reload the gun.   
$mag =$ magazine size.  The number of rounds in a full magazine.  
$bpsh =$ ammo per shot.  
$fac =$ target damage factor.  For kinetic damage, the factors are 1.0 for flesh and shields and 0.8 for armor.  
  
The time it takes to empty a full magazine (see Note 1):    $$\Large t_{firing}=\frac{mag}{fr \cdot  bpsh}$$  
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
See the section 'More on Procs' below for an illustration of how procs work. 

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
Doubles other damage types once a target is slagged.  8 second duration.  Even though slagging is said to double *all* other types of damage, for this app I just double the kinetic damage done while a target is slagged. For simplicities sake.   I've found that a good tactic with tough enemies is to slag them then switch to a gun that does more damage and pour it on. 

#### Explosive damage
Doubles kinetic damage.  Can cause splash explosive damage nearby targets. 

### Total DPS
The total DPS is simply:
$$\Large DPS=DPS_{kinetic}+DPS_{elemental}$$
The calculations above are repeated for each target type (flesh, shields and armor) and the results are shown in the main window.  An average of these 3 DPS numbers is also calculated and shown.  Since most elemental damage is based on chance, if you click on the 'Calculate' button repeatedly you will see differences in the resultant numbers each time for guns with elemental damage effects.  
	
## What isn’t included (yet)  
* Criticals
* Buffs for character, relic, class mods, etc…

## Supported systems
* MS Windows  

## More on Procs
Here is a visualization of the random nature of procs.  The elemental damage per second is 184 with a chance of 14.4% and a elemental duration of 8 seconds.   
![Figure_1](https://user-images.githubusercontent.com/11415077/180614648-583e38b4-dfdc-466a-95f8-ee07f1a48ed3.png)  
15 fire + reload cycles are shown.  The first proc triggers at ~10 ticks. Since the elemental damage is 184 dmg/sec the proc does about 61 dmg/tick. Just a few ticks later, another proc triggers and now we are seeing 122 dmg/tick. This increases again at ~20 ticks to 184 dmg/tick with 3 procs active.   At 34 ticks we see the first proc goes away after doing damage for 24 ticks (8 seconds).  This continues up and down for the rest of the 15 cycles as procs are triggered and expire.  
I ran the simulation again with the same inputs.   
![Figure_1a](https://user-images.githubusercontent.com/11415077/180615226-610873a8-8524-43ff-a95e-ff6c6f13c00f.png)  
This is a good illustration of how the random nature of procs can affect how effective your gun is every time you use it.  In this second run, the elemental damage starts on the first firing cycle and builds up to a mighty 550 dmg/tick before dropping down to a level more like the first example.  This is why I simulate 1000 cycles then average the damage over them all.    

## Notes  
[1] Let's says you have a magazine size of 5 and your gun uses 2 ammo per shot.  You should only get 2 shots per mag since after 2 shots you only have 1 round remaining.  But my tests show you get 3 shots.  Furthermore, you might think that extra shot would do half the normal damage since it would be one round instead of two.  But no, my tests show you get the same damage as a two round shot.   It appears that not only are shots per mag rounded up but an extra round is added from your inventory to make the shot a full two round shot.  
