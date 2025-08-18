# PFCMainArcSorting
Repo for sorting code to place players into their desired Main Arc campaign.  
**You shouldn't have to edit the code at all, it should get everything from the .csv file that you give it.**  
  - You will have to edit the sheet linked to the form slightly before opening it, which is described more in the "Notes" section  

API: python MainArcSort.py -s [EXCEL_SPREADSHEET_NAME].csv  
(This is what you put into the command line in order to run the program)  
(Fill in [EXCEL_SPREADSHEET_NAME] with whatever the spreadsheet name is)  

Heres the link to the template form:  
https://docs.google.com/forms/d/1LwCmqdsbEx-Xj2Fzpx_EXjGeGwG1yJpDu_SrBFwpZNs/edit  

### Notes:
- To customize the template form to the current Main Arcs, please make a copy of it and use that.
- The first submission should be edited on the linked sheet to put the cap of each campaign where the ranking would usually be.
  - The program ignores the first line after it has obtained the Campaign Caps.

### Assumptions:
- It is assumed that you have gone through and verified/cleaned the groups.
  - To do this just make sure that the pairs line up, and delete any answers that do not.
- It is also assumed that you do not change the template.
  - The backend should have 3 columns before (Timestamp/PlayerName/CharName) and 3 columns (WantedPlayer1/2/UnwantedPlayer(s)) after the campaigns so the code can grab the indexes without issue.
