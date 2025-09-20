# PFCMainArcSorting
Repo for sorting code to place players into their desired Main Arc campaign.  
**You shouldn't have to edit the code at all, it should get everything from the .csv file that you give it.**  
  - You will have to edit the sheet linked to the form slightly before opening it, which is described more in the "Notes" section
  - If you wish to edit the strength of splitting Unpreffered/Friendship pairs, use ctrl+f and search 'UPDATE:' in the code
  - If the code ever breaks, hope and pray that there is a lovely student in club or discord to take a look at it. The contributors herein (as you can see through the "commits" section in GitHub) are likely more than willing to do so. 

**API**: python MainArcSort.py -s <RESPONSE_SHEET>.csv [-b <BLACKLIST>.csv]  
(This is what you put into the command line in order to run the program)  
(Fill in <RESPONSE_SHEET> with whatever the spreadsheet name is)  
(Fill in <BLACKLIST> with whatever the blacklist name is, if desired)

### How to Run:
Run the code in some sort of Python IDE copy-pasting the above API in the terminal.
I used **VS Code**, but it shouldn't be required.
Once you have the code within the IDE:
1. Open the terminal
2. Make sure that both the code and excel spreadsheet are in the same file location
  - ie. C:\Users\bob\downloads
  - If they aren't, use file explorer to put them in the same location (or if you have knowledge of how to run files from termianl, then just do that)
  - Make sure you are opening the file from the right location aswell, otherwise it'll be upset and won't run
3. Run the code

## How to Read the Output:
It will print out multiple things:

1. Status:
  - Optimal is good. That means everything worked perfectly!
2. Cost (Lower is Better)
  - This will always be greater than 0. 
  - Only really worry about this if constraints are becoming a problem. 
3. Each campaign will print out: Name (Occupancy / Capacity): List of [Name (Discord Username)]

Then Constraints:
4. Friendship Pairs and whether they were upheld
5. Unpreferred People and whether they were put in the same campaign
6. [If a blacklist is present] Each blacklist item and wether the ban was violated

## Setup
[Here's the link to the template form.](https://docs.google.com/forms/d/1LwCmqdsbEx-Xj2Fzpx_EXjGeGwG1yJpDu_SrBFwpZNs/edit)

### Notes
- To customize the template form to the current Main Arcs, please make a copy of it and use that.
- The first submission should be edited on the linked sheet to put the cap of each campaign where the ranking would usually be.
  - The program ignores the first line after it has obtained the Campaign Caps.

### Assumptions:
- It is assumed that you have gone through and verified/cleaned the groups/unpreffered people.
  - To do this just make sure that the pairs line up, and delete any answers that do not.
  - Any names in the last 3 columns of the excel spreadsheet should match to 1 in the "Player name" section. Delete/edit them if not.
- It is also assumed that you do not change the template.
  - The backend should have 3 columns before (Timestamp/PlayerName/CharName) and 3 columns (WantedPlayer1/2/UnwantedPlayer(s)) after the campaigns so the code can grab the indexes without issue.

### Some Caviats:
- This optimizer is based on an LP minimization algorithm. (Wikipedia has a good explanation if you care.)
- The cost is based on minimizing the sum of rankings and number of held frendshipts both without violating constraints. 
- Since the algorithm is deterministic, technically the ordering of filling out the response can matter. It only matters to a *tiny* degree though. If my calculations are correct ☝️🤓, this should mean that it is better to fill out the response form earlier. Since the constraints and rankings are very complex, the effect should be minimal. Just a caviat we should always keep in mind. *I may add a "true" random mode to remove this effect, but don't quote me on that plx.* 
