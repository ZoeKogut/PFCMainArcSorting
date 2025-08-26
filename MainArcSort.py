import pulp as pl
import pandas as pd
import argparse as ap

# NOTE:
# This is made for the 2025 Newbie campaign: To change for following years,
# Seach "UPDATE:" in the search bar and follow the directions.

# API: python MainArcSort.py -s [EXCEL_SPREADSHEET_NAME].csv

# ---------------------------------------------------------------------
# 1)  SAMPLE DATA  ----------------------------------------------------
# ---------------------------------------------------------------------
parser = ap.ArgumentParser(description='PFC: Main Arc Sorting')
parser.add_argument('-s', '--sheet', type=str, required=True, help='Excel Spreadsheet in CSV format')
args = parser.parse_args()

data = pd.read_csv(args.sheet, converters={"Player Name": str, "Preferred Person 1": str, "Preferred Person 2": str, "Unprefered People": str}) #Turns column labled Player Name into a str.
# Remove leading and trailing spaces
data['Player Name'] = data['Player Name'].str.strip()
data['Preferred Person 1'] = data['Preferred Person 1'].str.strip()
data['Preferred Person 2'] = data['Preferred Person 2'].str.strip()
data['Unprefered People'] = data['Unprefered People'].str.strip()

#print(data.head)
##Might need other columns to be labled string too (Preffered Player 1 and 2 specifically)
## Replace N/A with 10 in data (so that they are labled as "last picks")

#Get the number of columns, then subtract 6 
#   (4 at the front: Timestamp, PlayerName, DiscordUser, CharacterName)
#   (3 at the end: WantedPlayer1, WantedPlayer2, UnwantedPlayer(s))
campaign_numb = len(data.columns) - (4 + 3)
indexes = []
for x in range(4, (campaign_numb+4)): #4 is added because we want the colm numbers of the dataframe, and we're skipping the first 4 colms
    indexes.append(x)
#print(indexes)

campaigns = data.iloc[:, indexes].columns.tolist() #Obtain Campaign Names

# capacity of each Campaign
# TODO: Possibly update this with an option for people to break caps depending on total # of newbies?
capacity = data.iloc[0, indexes].to_dict()
data = data.iloc[1:] #Removes the capacity row
students_df = data.iloc[:, 1] #Have this take from the Student section of the Excel Sheet
students = students_df.tolist()
#print(students)

discord_tags = dict(zip(data["Player Name"], data["Discord Username"])) 
    #This is used to print out the tag along with the campaign assignments

#   rank[i][j] = how student i ranks house j  (1 = best, larger = worse)
#This will be inputted from the excel spreadsheet, look within data
rank_df = data.iloc[:, indexes] # Selects the Player name column + the campaign name columns
rank_df = rank_df.fillna(value=10) # Fill every unfilled value with 10 (ranked last) (All have equal chance of being filled if it gets to that)
rank_indexes = []
for x in range(0, campaign_numb): #4 is added because we want the colm numbers of the dataframe, and we're skipping the first 4 colms
    rank_indexes.append(x)

print(rank_indexes)
rank = {}
rank_temp = {}
for x in range(len(rank_df.index)):
    rank_temp = dict(zip(campaigns,rank_df.iloc[x,rank_indexes])) #Make every rank into a dictionary
    rank[students_df.iloc[x]] = (rank_temp) #Add ^^ dictionary as the value associated w/ the name in the [Rank] dictionary


friends_df = data.iloc[:, [1,(len(data.columns) - 3),(len(data.columns) - 2)]] #Grabing the 1st, 3rd to last, and 2nd to last columns 
friends_df = friends_df.replace('', "NONE")

unpreferred_df = data.iloc[:, [1,(len(data.columns) - 1)]] #Grabing the 1st and last columns 
unpreferred_df = unpreferred_df.replace('', "NONE") #replace empty w/ NONE to make it easier to ignore these
unpreffered_pairs = [] #undirected
#print(unpreferred_df)

for x in range(len(unpreferred_df.index)): 
    name = unpreferred_df.iloc[x, 0]
    unprefPerson = unpreferred_df.iloc[x, 1]
    
    #Check if the first Name,uPP is in the unpreffered_pairs list already
    if (unprefPerson != "NONE"):
        unpreffered_pairs_list = unprefPerson.split(',') #the unpreferred people is a list, so split on the comma
        for person in unpreffered_pairs_list:
            person = person.strip()
            if (not (((name,person) in unpreffered_pairs))): 
                unpreffered_pairs.append((name,person))
    

friend_pairs = []  # undirected
for x in range(len(friends_df.index)): 
    name = friends_df.iloc[x, 0]
    prefPerson1 = friends_df.iloc[x, 1]
    prefPerson2 = friends_df.iloc[x, 2]

    #Check if the first Name,PP1 is in the friends list already
    if (prefPerson1 != "NONE"):
        if (not (((name,prefPerson1) in friend_pairs) or ((prefPerson1, name) in friend_pairs))): 
            friend_pairs.append((name,prefPerson1))
    
    #Check if the second Name,PP2 is in the friends list already
    if (prefPerson2 != "NONE"):
        if (not (((name,prefPerson2) in friend_pairs) or ((prefPerson2, name) in friend_pairs))): {
            friend_pairs.append((name,prefPerson2))
        }


#UPDATE: If you need to change the weight of Unpreffered and Preferred pairs, change Lambda_1 and Lambda_2
        # Lambda_1 correlates to Friendship Pairs (the larger the number, the worse penalty you take for splitting them)
        # Lambda_2 correlates to Unpreffered Pairs (the more negative the number, the bigger bonus you get for splitting them)

lambda_1 = (len(rank_df) + 1)  # weight: how many “rank points” is splitting a pair worth?
            # ^^ Splitting the pair will be the same as putting someone in their worst ranked pick (+1)
lambda_2 = -5                  # weight: how many points is splitting an unpreferred pair worth
            # ^^ Dont really have a number that would make this the "worst" option considering its like. A negative number. 
            #  Ig it can be increased if theres still people not being put together


# ---------------------------------------------------------------------
# 2)  MODEL  ----------------------------------------------------------
# ---------------------------------------------------------------------
prob = pl.LpProblem("Main_Arc_Sorting", pl.LpMinimize)

# Binary assignment vars: x[i,j] = 1 ↔ player i put in campaign j
x = pl.LpVariable.dicts("x", (students, campaigns), cat="Binary")

# Binary separation vars for each friendship pair
delta_1 = pl.LpVariable.dicts("delta", friend_pairs, cat="Binary")

# Binary separation vars for each unpreffered pair
delta_2 = pl.LpVariable.dicts("delta_unpref", unpreffered_pairs, cat="Binary")

# --- Objective -------------------------------------------------------
preference_cost = pl.lpSum(rank[i][j] * x[i][j] for i in students for j in campaigns) 
    #^^ This multiplies the rank for each person by the cost for putting them in said campaign.
    #So at the end it should be "the cost for putting I person in J campaign"
friend_cost     = pl.lpSum(lambda_1 * delta_1[p] for p in friend_pairs)
unpref_cost     = pl.lpSum(lambda_2 * delta_2[p] for p in unpreffered_pairs) 
    #there is the option to make the unpreffered_pairs subtracted from the total. might be better
prob += preference_cost + friend_cost + unpref_cost

# --- Constraints -----------------------------------------------------
# (1) each student assigned to exactly one campaign
for i in students:
    prob += pl.lpSum(x[i][j] for j in campaigns) == 1, f"OneCampaign_{i}"

# (2) campaign capacity respected
for j in campaigns:
    prob += pl.lpSum(x[i][j] for i in students) <= capacity[j], f"Cap_{j}"

# (3) linearise “split?” for every friendship pair (i,k)
#     delta1_{ik} ≥ |x_{i,j} - x_{k,j}|  for all j
for (i, k) in friend_pairs:
    for j in campaigns:
        prob += delta_1[(i, k)] >= x[i][j] - x[k][j] #Wanted is 1-1 to equal 0, but at most it will equal 1 (1-0)
        prob += delta_1[(i, k)] >= x[k][j] - x[i][j]

for (i, k) in unpreffered_pairs:
    for j in campaigns:
        prob += delta_2[(i, k)] >= x[i][j] + x[k][j] #refersed the signs. have no clue if thats how this works kekwwww
        prob += delta_2[(i, k)] >= x[k][j] + x[i][j] # Add together, ie 0 + 1 or 0 + 0, you want delta to be greater though, so 1+1 would be bad


# ---------------------------------------------------------------------
# 3)  SOLVE  ----------------------------------------------------------
# ---------------------------------------------------------------------
prob.solve(pl.PULP_CBC_CMD(msg=False))
print(f"Status : {pl.LpStatus[prob.status]}")
print(f"Total cost = {pl.value(prob.objective):.0f}\n")

# pretty-print assignment
by_campaign = {j: [] for j in campaigns}
for i in students:
    name_and_tag = i + " (" + discord_tags[i] + ")"
    for j in campaigns:
        if pl.value(x[i][j]) > 0.5:
            by_campaign[j].append(name_and_tag)

for j in campaigns:
    print(f"{j} ({len(by_campaign[j])}/{capacity[j]}): {', '.join(by_campaign[j])}")

print("\nFriendship splits:")
for (i, k) in friend_pairs:
    split = int(pl.value(delta_1[(i, k)]))
    same  = "Correct" if split == 0 else "Split" 
    print(f" {i}-{k}: {'same campaign:' if split == 0 else 'different campaign:'} {same}")

print("\nUnpreffered splits:")
for (i, k) in unpreffered_pairs:
    split = int(pl.value(delta_2[(i, k)]))
    same  = "Wrong" if split == 0 else "Correct" 
    print(f" {i}-{k}: {'same campaign:' if split == 0 else 'different campaign:'} {same}")

#"""

