import pandas as pd

#Improting all the CSV and combining them into one dataframe 
df = pd.concat([
    pd.read_csv("pixie_data/pixie_1.csv"),
    pd.read_csv("pixie_data/pixie_2.csv"),
    pd.read_csv("pixie_data/pixie_3.csv"),
    pd.read_csv("pixie_data/pixie_4.csv"),
    pd.read_csv("pixie_data/pixie_5.csv")
], ignore_index=True)

print(df)

#Turning the timestamps into datatime values
df["@timestamp"] = pd.to_datetime(
    df["@timestamp"],
    format="%b %d, %Y @ %H:%M:%S.%f"
)

#From event column only keep game start and game end 
games = df[df["event"].isin(["GAME_START", "GAME_END"])].copy()

#creates a new dataframe with only the game start 
starts = games[games["event"] == "GAME_START"].copy()

#Creates a new dataframe with only the game end 
ends = games[games["event"] == "GAME_END"].copy()

#Rename the timestamp column to game start and generic string to game name in the start dataframe 
starts = starts.rename(columns={
    "@timestamp": "game_start",
    "generic_string": "game_name"
})

#rename the timestamp column to game end and generic string to game name in the end dataframe 
ends = ends.rename(columns={
    "@timestamp": "game_end",
    "generic_string": "game_name"
})

#Sort the hostname to have the corresponding game name and game start 
starts = starts.sort_values(["hostname", "game_name", "game_start"])

#creates a new column called next_game_start to store when does the same game start again on the same pixie 
starts["next_game_start"] = (

    #groups the hostname and game name and looks at game start
    starts.groupby(["hostname", "game_name"])["game_start"]

    #Moves the start time one row up so each start time can be compared to the next start time for the same game on the same pixie
    .shift(-1)
)

#create a new dataframe called session to match game start and game end to correct game name and hostname 
sessions = pd.merge_asof( #matches rows based on date and time 
    
    #sorts the start dataframe with the game start 
    starts.sort_values("game_start"),

    #Sorts the end data frame with game end
    ends.sort_values("game_end"),

    #Makes it so the game start is the starting point to find the match 
    left_on="game_start",

    #Looks for the matching game end that corresponds to the game start 
    right_on="game_end",

    #matches the game start and end to the correct hostname and game name, only when hostanme and game name are same 
    by=["hostname", "game_name"],

    #Looks for the game end time after the game start time 
    direction="forward"
)

#It fixes the issue from previous step where the game end time is not the correct game end for the game start 
sessions.loc[ #find specific row and a specific column 
    
    #Looks if there is another game start, check in the game_next column 
    sessions["next_game_start"].notna() &

    #Is the matched game end happening at or after the next game start for the same game, if true then game end was matched wrongly 
    (sessions["game_end"] >= sessions["next_game_start"]),

    #only chnage game end 
    "game_end"

    #if any missing value replace with NaT
] = pd.NaT

#removes the next game start column from the dataframe
sessions = sessions.drop(columns=["next_game_start"])

#maps out the location for each pixie based on the hostname 
location_map = {
    "p-03cbbcb4f4d3": "Zurich, Switzerland, Europe",
    "p-03cbbcb7d615": "Melbourne, Australia, Oceania",
    "p-03cbbd5b87c0": "France, Europe",
    "p-03cbbd5b9347": "France, Europe",
    "p-03cbbd5bd5b3": "Switzerland, Europe"
}

#For each hostname look for the correct location in the location map 
sessions["location"] = sessions["hostname"].map(location_map)

#find the total minutes played for each game session and rounds it up to 2 decimal places 
sessions["total_minutes"] = (
    (sessions["game_end"] - sessions["game_start"])
    .dt.total_seconds() / 60
).round(2)

#keeps only the column names wanted for the final dataframe 
sessions = sessions[
    ["hostname",
     "game_name",
     "game_start",
     "game_end",
     "total_minutes",
     "location"]
]

print(sessions.head(20))