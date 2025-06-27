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

data = pd.read_csv(args.sheet, converters={"Player Name": str}) #Turns column labled Player Name into a str.
##Might need other columns to be labled string too (Preffered Player 1 and 2 specifically)
## Replace N/A with 10 in data (so that they are labled as "last picks")

indexes = [3,4,5,6,7,8,9,10,11]
#UPDATE: Update the campaign names here to match the names in [capacity] and on the excel sheet
campaigns = data.iloc[:, indexes].columns.tolist() #Obtain Campaign Names
#print(campaigns)

# capacity of each Campaign
    #UPDATE: Update this when people have limits for their campaigns
    #Also Update names to match the ones in [campaigns]
# TODO: Possibly update this with an option for people to break caps depending on total # of newbies?
capacity = data.iloc[0, indexes].to_dict()
data = data.iloc[1:] #Removes the capacity row
students_df = data.iloc[:, 1] #Have this take from the Student section of the Excel Sheet
students = students_df.tolist()
print(students)

#   rank[i][j] = how student i ranks house j  (1 = best, larger = worse)
#This will be inputted from the excel spreadsheet, look within data
rank_df = data.iloc[:, [3,4,5,6,7,8,9,10,11]] # Selects the Player name column + the campaign name columns
rank_df = rank_df.fillna(value=10) # Fill every unfilled value with 10 (ranked last) (All have equal chance of being filled if it gets to that)
rank = {}
rank_temp = {}
for x in range(len(rank_df.index)):
    rank_temp = dict(zip(campaigns,rank_df.iloc[x,[0,1,2,3,4,5,6,7,8]])) #Make every rank into a dictionary
    rank[students_df.iloc[x]] = (rank_temp) #Add ^^ dictionary as the value associated w/ the name in the [Rank] dictionary


# friendship (“try to keep us together”) pairs
# TODO: Update friend_pairs with the correct equation
"""
-Pair for each person 1 and 2
-IF: if already in the list, skip
-If not, add the pair
-If NAN, skip too
"""
friends_df = data.iloc[:, [1,12,13]]
friends_df = friends_df.fillna(value="NONE")
#print(friends_df)
#print(friends_df.iloc[2, 1])

friend_pairs = []  # undirected
for x in range(len(friends_df.index)): 
    name = friends_df.iloc[x, 0]
    prefPerson1 = friends_df.iloc[x, 1]
    prefPerson2 = friends_df.iloc[x, 2]

    #Check if the first Name,PP1 is in the friends list already
    if (prefPerson1 != "NONE"):
        if (not (((name,prefPerson1) in friend_pairs) or ((prefPerson1, name) in friend_pairs))): 
            friend_pairs.append((name,prefPerson1))
    
    #Check if the second Name,PP1 is in the friends list already
    if (prefPerson2 != "NONE"):
        if (not (((name,prefPerson2) in friend_pairs) or ((prefPerson2, name) in friend_pairs))): {
            friend_pairs.append((name,prefPerson2))
        }

# TODO: Add enemy pairs ("Do not put us together")

lambda_1 = 2        # weight: how many “rank points” is splitting a pair worth?
# For enemy pairs would putting the lambda as negative work?
    # "Points for putting these together"

# ---------------------------------------------------------------------
# 2)  MODEL  ----------------------------------------------------------
# ---------------------------------------------------------------------
prob = pl.LpProblem("Main_Arc_Sorting", pl.LpMinimize)

# Binary assignment vars: x[i,j] = 1 ↔ player i put in campaign j
x = pl.LpVariable.dicts("x", (students, campaigns), cat="Binary")

# Binary separation vars for each friendship pair
delta_1 = pl.LpVariable.dicts("delta", friend_pairs, cat="Binary")

# --- Objective -------------------------------------------------------
preference_cost = pl.lpSum(rank[i][j] * x[i][j] for i in students for j in campaigns) 
    #^^ This multiplies the rank for each person by the cost for putting them in said campaign.
    #So at the end it should be "the cost for putting I person in J campaign"
friend_cost     = pl.lpSum(lambda_1 * delta_1[p] for p in friend_pairs)
prob += preference_cost + friend_cost

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
        prob += delta_1[(i, k)] >= x[i][j] - x[k][j]
        prob += delta_1[(i, k)] >= x[k][j] - x[i][j]

# ---------------------------------------------------------------------
# 3)  SOLVE  ----------------------------------------------------------
# ---------------------------------------------------------------------
prob.solve(pl.PULP_CBC_CMD(msg=False))
print(f"Status : {pl.LpStatus[prob.status]}")
print(f"Total cost = {pl.value(prob.objective):.0f}\n")

# pretty-print assignment
by_campaign = {j: [] for j in campaigns}
for i in students:
    for j in campaigns:
        if pl.value(x[i][j]) > 0.5:
            by_campaign[j].append(i)

for j in campaigns:
    print(f"{j} ({len(by_campaign[j])}/{capacity[j]}): {', '.join(by_campaign[j])}")

print("\nFriendship splits:")
for (i, k) in friend_pairs:
    split = int(pl.value(delta_1[(i, k)]))
    same  = "Correct" if split == 0 else "Split" 
    print(f" {i}-{k}: {'same campaign' if split == 0 else 'split'} {same}")

#"""
