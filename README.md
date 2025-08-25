# PFCMainArcSorting
Repo for sorting code to place players into their desired Main Arc campaign.  
**You shouldn't have to edit the code at all, it should get everything from the .csv file that you give it.**  
  - You will have to edit the sheet linked to the form slightly before opening it, which is described more in the "Notes" section
  - If you wish to edit the strength of splitting Unpreffered/Friendship pairs, use ctrl+f and search 'UPDATE:' in the code

**API**: python MainArcSort.py -s [EXCEL_SPREADSHEET_NAME].csv  
(This is what you put into the command line in order to run the program)  
(Fill in [EXCEL_SPREADSHEET_NAME] with whatever the spreadsheet name is)  

### How to Run:
Run the code in some sort of Python IDE copy-pasting the above API in the terminal.
I used **VS Code**, but it shouldn't be required.
Once you have the code within the IDE:
- Open the terminal
- Make sure that both the code and excel spreadsheet are in the same file location
  - ie. C:\Users\bob\downloads
  - If they aren't, use file explorer to put them in the same location (or if you have knowledge of how to run files from termianl, then just do that)
  - Make sure you are opening the file from the right location aswell, otherwise it'll be upset and won't run
- Run the code
  - It will print out multiple things,
    - the Unpreffered Pairs and Friendship pairs are there so you can verify that everyone is grouped as intended
    - The Campaigns will print out with a list of the people within each, along with the name of the campaign

Heres the link to the template form:  
https://docs.google.com/forms/d/1LwCmqdsbEx-Xj2Fzpx_EXjGeGwG1yJpDu_SrBFwpZNs/edit  

### Notes:
- To customize the template form to the current Main Arcs, please make a copy of it and use that.
- The first submission should be edited on the linked sheet to put the cap of each campaign where the ranking would usually be.
  - The program ignores the first line after it has obtained the Campaign Caps.

### Assumptions:
- It is assumed that you have gone through and verified/cleaned the groups/unpreffered people.
  - To do this just make sure that the pairs line up, and delete any answers that do not.
  - Any names in the last 3 columns of the excel spreadsheet should match to 1 in the "Player name" section. Delete/edit them if not.
- It is also assumed that you do not change the template.
  - The backend should have 3 columns before (Timestamp/PlayerName/CharName) and 3 columns (WantedPlayer1/2/UnwantedPlayer(s)) after the campaigns so the code can grab the indexes without issue.
