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

data = pd.read_csv(args.data, converters={'Person': str}) #Have a column labled Person.

students = data["Person"] #Have this take from the Student section of the Excel Sheet
#UPDATE: Update the campaign names here to match the names in [capacity]
campaigns = ["H1", "H2", "H3"] #Campaign Names or Number, whichever the sheet puts into the backend

# capacity of each Campaign
    #UPDATE: Update this when people have limits for their campaigns
    #Also Update name
# TODO: Possibly update this with an option for people to break caps depending on total # of newbies?
capacity = {"H1": 2, "H2": 2, "H3": 2} 

#   rank[i][j] = how student i ranks house j  (1 = best, larger = worse)
#This will be inputted from the excel spreadsheet, look within data
# TODO: Update rank with the correct equation
# Should be able to just put dataframe, "Student Name/Column: {[Campaign Name]: [rank], etc}"
rank = {
    "A": {"H1": 1, "H2": 2, "H3": 3},
    "B": {"H1": 1, "H2": 2, "H3": 3},
    "C": {"H1": 2, "H2": 1, "H3": 3},
    "D": {"H1": 3, "H2": 1, "H3": 2},
    "E": {"H1": 3, "H2": 2, "H3": 1},
    "F": {"H1": 2, "H2": 3, "H3": 1},
}

# friendship (“try to keep us together”) pairs
# TODO: Update friend_pairs with the correct equation
friend_pairs = {("A", "B"), ("C", "D"), ("E", "F")}  # undirected

# TODO: Add enemy pairs

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
sigma_1 = pl.LpVariable.dicts("delta", friend_pairs, cat="Binary")

# --- Objective -------------------------------------------------------
preference_cost = pl.lpSum(rank[i][j] * x[i][j] for i in students for j in campaigns)
friend_cost     = pl.lpSum(lambda_1 * sigma_1[p] for p in friend_pairs)
prob += preference_cost + friend_cost

# --- Constraints -----------------------------------------------------
# (1) each student assigned to exactly one campaign
for i in students:
    prob += pl.lpSum(x[i][j] for j in campaigns) == 1, f"OneCampaign_{i}"

# (2) campaign capacity respected
for j in campaigns:
    prob += pl.lpSum(x[i][j] for i in students) <= capacity[j], f"Cap_{j}"

# (3) linearise “split?” for every friendship pair (i,k)
#     sigma1_{ik} ≥ |x_{i,j} - x_{k,j}|  for all j
for (i, k) in friend_pairs:
    for j in campaigns:
        prob += sigma_1[(i, k)] >= x[i][j] - x[k][j]
        prob += sigma_1[(i, k)] >= x[k][j] - x[i][j]

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
    split = int(pl.value(sigma_1[(i, k)]))
    same  = "Correct" if split == 0 else "Split" 
    print(f" {i}-{k}: {'same campaign' if split == 0 else 'split'} {same}")