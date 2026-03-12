import time
from flask import Flask, render_template, request, jsonify
import pandas as pd
from flask_cors import CORS, cross_origin
from datetime import datetime
import os
import sys
import openai
import sqlite3
import json
import pickle
from alpaca_trade_api import TimeFrame as tf

from util import portfolio_util as port_util, alpaca_util as alpaca
from ML4TE import marketsimcode_v2 as mk

import numpy as np
from copy import deepcopy
import requests
from datetime import datetime
from dateutil import tz
import pytz


app = Flask(__name__)
cors = CORS(app)
CORS(
    app,
    resources={r"/api/*": {"origins": ["https://alexanderferrara.com", "http://localhost:3000"]}},
    supports_credentials=True,
)
app.config["CORS_HEADERS"] = "Content-Type"
#alpaca.cache_init()
app.config["DEBUG"] = True

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/catan')
def catan():
    return render_template("catan-trading-bloc.html")

@app.route('/eli-ai')
def eliai():
    return render_template("eli-ai.html")

@app.route('/dog-door')
def dogdoor():
    return render_template("dog-door.html")

@app.route('/ML4Stonks')
def ML4TE():
    return render_template("stonks.html")

@app.route('/stonk-modeler')
def stonk_modeler():
    return render_template("modeler.html")

@app.route('/summarize-ai')
def summarize():
    return render_template("summarize-ai.html")

@app.route('/sba')
def get_sba():
    return render_template("sba.html")

@app.route('/time')
def get_current_time():
    return {'time': time.time()}

@app.route('/test')
def get_current_test():
    return {'test1': "test2", 'test69' : 69}

@app.route('/data/<fname>')
@cross_origin()
def get_compare(fname):
    data = pd.read_csv("./data/"+fname+".tsv", sep='\t')
    data = data.to_csv(sep="\t")
    print("./data/"+fname+".tsv")
    print(data)
    return data

@app.route('/eli_prompt', methods = ['POST'])
@cross_origin()
def eli_prompt():

    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        input_str = request.form['prompt']
        comp_level = request.form['age']
        comp_level = comp_level + " year old"
        language = "English"

        prompt =  "Explain "+input_str+" at the reading and comprehension level of a "+comp_level+" in the " + language + " language"
        print(prompt)

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=255,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        log_str = "Prompt: "+input_str+" | "+comp_level+" | "+language+"\n"
        log_str += "Reponse: "+response.choices[0]["text"].lstrip()+"\n"
        write_log("eli-ai",log_str)

        return response.choices[0]["text"]

    except:
        return "Whoops... something failed. Please check your connection and try again."


@app.route('/summarize_prompt', methods = ['POST'])
@cross_origin()
def summarize_prompt():
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        input_str = request.form['prompt']

        comp_level = request.form['age']

        prompt =  "Summarize the following in "+comp_level+" words or less: \""+ input_str +"\""
        print(prompt)

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            temperature=0.7,
            max_tokens=255,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    except:
        return "Whoops... something failed. Please check your connection and try again."
    print(response)

    log_str = "Prompt: "+input_str+" | "+comp_level+" | "+"\n"
    log_str += "Reponse: "+response.choices[0]["text"].lstrip()+"\n"
    write_log("xWoL",log_str)

    return response.choices[0]["text"]

# Stonk App Supporting API Functions #
"""
API Function to pull stock data for given time period and return frontend ready data for table and CLOSE charting
"""
@app.route('/stonks', methods = ['POST'])
@cross_origin()
def stonk_data():
    print("Stonk Data Request Received")
    response = [0,0,0]
    try:
        symbol, sd, ed = stonk_sanitize(request)
        response = alpaca.get_prices(symbol,sd,ed, tf=tf.Day, crypto=False)#['close']
    except:
        return "Whoops... something failed. Please check your connection and try again."
    print(response)

    write_log("stonk","shit to log about data request here")

    html = response.to_html(index_names=False)
    x = response.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
    y = response["close"].values.tolist()

    return (jsonify({'x': x, 'y':y, 'html': html}))#(orient="records"))

"""
API Function to accept a model training request and kick it off using ML4T backend shit
"""
@app.route('/stonk_model_train', methods = ['POST'])
@cross_origin()
def stonk_model_train():
    print("Stonk Model Train Request Received")

    try:
        symbol, sd, ed = stonk_sanitize(request)
        inds = json.loads(request.form["inds"])
        # model = MARKETSIM OR SOME SHIT LIKE THAT HERE USING THE ABOVE
        # response = model.query(outsample) or separate functions?

        model_id, model = mk.train_model(symbols = [symbol], start_date_in 	= sd, end_date_in 	= ed)


    except:
        return "Whoops... something failed. Please check your connection and try again."
    print(model_id)

    write_log("stonk","shit to log about training request here")

    return (jsonify({'model_id': model_id}))


"""
API Function to accept a model training request and kick it off using ML4T backend shit
"""
@app.route('/stonk_model_test', methods = ['POST'])
@cross_origin()
def stonk_model_test():
    print("Stonk Model Train Request Received")

    try:
        symbol, sd, ed = stonk_sanitize(request)

        model_id = request.form["model"]
        # model = MARKETSIM OR SOME SHIT LIKE THAT HERE USING THE ABOVE
        # response = model.query(outsample) or separate functions?
        file_loc = "src/stonk_data/trained_models/"+model_id+".pickle"
        file_handle = open(file_loc,"rb")
        sl = pickle.load(file_handle)
        file_handle.close()

        results = mk.test_model(sl, symbols = [symbol], sd = sd, ed = ed)


    except:
        return "Whoops... something failed. Please check your connection and try again."
    print(model_id)

    write_log("stonk","shit to log about training request here")

    bmx = results["bm"]["portvals"].index.strftime("%Y-%m-%d %H:%M:%S").tolist()
    bmy = (results["bm"]["portvals"]/100000).values.tolist()

    slx = results["sl"]["portvals"].index.strftime("%Y-%m-%d %H:%M:%S").tolist()
    sly = (results["sl"]["portvals"]/100000).values.tolist()

    bmstats = results["bm"]["stats"]
    slstats = results["sl"]["stats"]

    return (jsonify({'bmx': bmx, 'bmy':bmy, "slx":slx, "sly":sly, "bmstats":bmstats, "slstats":slstats}))


"""
API Function to dump contents of models database into an HTML table
"""
@app.route('/stonk_model_db_all', methods = ['POST'])
@cross_origin()
def stonk_model_db_all():
    print("Stonk model db dump request received")

    try:
        sqliteConnection = sqlite3.connect('src/stonk_data/models.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        cols = ["MODEL_ID", "START_DATE", "END_DATE", "SYMBOL", "BINS", "TIMEFRAME", "CRYPTO"]
        hidden = [False, False, False, False, True, True, True]

        sqlite_query = " SELECT "+','.join(cols)+" FROM MODELS "
        cursor.execute(sqlite_query)
        rows = cursor.fetchall()
        print("Model inserted successfully as a BLOB into a table")
        cursor.close()

        return html_table(rows,cols,hidden)

        dictified = []
        for row in rows:
            d_row = {}
            for ind, cell in enumerate(row):
                d_row[cols[ind]] = cell
            dictified.append(d_row)

        return jsonify({'data': dictified})

    except:
        return "Whoops... something failed. Please check your connection and try again."

def write_log(fname, contents):
    # Append-adds to log file
    now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    target = "src/logs/"+fname+".log"
    print("writing to:", target)
    file1 = open(target, "a+", encoding="utf-8")  # append mode
    file1.write("----------------------------------------------\n")
    file1.write(now+"\n")
    file1.write(contents+"\n")
    file1.close()

def stonk_sanitize(request):
    symbol = request.form['prompt']
    if symbol == "":
        symbol = "GME"
    sd = request.form['sd']
    if sd == "":
        sd = "2017-08-01"
    ed = request.form['ed']
    if ed == "":
        ed = "2019-09-02"
    return symbol, sd, ed

def html_table(table, headers, hidden):
    out = ""
    out += '<table><thead><tr><th></th>'
    for ind, header in enumerate(headers):
        hide = ""
        if hidden[ind]:
            hide = "class = none"
        out += "<th "+ hide +">"+header+"</th>"
    out += '</tr></thead><tbody>'
    for row in table:
        out += '  <tr><td class="dt-control"></td>'
        for cell in row:
            out += "<td>"+str(cell)+"</td>"
        out += '</tr>'
    out += '</tbody></table>'
    return out








### Starting Dog Door Section ###
def send_request(url):
    print("requesting url: " + url)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
    except Exception as e:
        print("Error: ", e)
        return e
    return 1

@app.route('/dd-open', methods = ['POST'])
def open_door():
    send_request("http://136.38.28.80/?direction=forward")
    time.sleep(2.4*5)
    send_request("http://136.38.28.80/?direction=stop")
    return "open attempted"

@app.route('/dd-close', methods = ['POST'])
def close_door():
    send_request("http://136.38.28.80/?direction=reverse")
    time.sleep(2.8*5)
    send_request("http://136.38.28.80/?direction=stop")
    return "close requested"

### Ending Dog Door Section












### Starting SBA Section ###

### Helper Functions ###
def arbable(p1, p2):
    return ((1 / p1) * 100) + ((1 / p2) * 100) < 100

def balance_stakes(p1, p2):
    bet_pct1 = 100*(p2) / (p1 + p2)
    bet_pct2 = 100-bet_pct1
    return (bet_pct1, bet_pct2)


def outcomes(p1, p2, stk1, stk2):
    outcome1 = (p1 * stk1) - (stk1 + stk2)
    outcome2 = (p2 * stk2) - (stk1 + stk2)
    return (outcome1, outcome2)

def dec_to_amer_odds(decimal_odds):
    if decimal_odds >= 2.0:
        american_odds = (decimal_odds - 1) * 100
    else:
        american_odds = -100 / (decimal_odds - 1)
    return round(american_odds)

def printline(line):
    out = ""
    out += line['name'] + " "
    if "point" in line:
        out += str(line["point"]) + " "
    out += "@ "
    if line["price"] > 0:
        out += "+"
    out += str(line["price"])
    return out

def convert_to_eastern_time(iso_datetime):
    # Parse the ISO datetime string
    dt = datetime.strptime(iso_datetime, '%Y-%m-%dT%H:%M:%S%z')

    # Set the timezone to UTC
    utc_timezone = tz.gettz('UTC')
    dt = dt.replace(tzinfo=utc_timezone)

    # Convert to Eastern Time
    eastern_timezone = tz.gettz('America/New_York')
    dt_eastern = dt.astimezone(eastern_timezone)

    # Format the datetime as desired
    formatted_datetime = dt_eastern.strftime('%m/%d/%Y\n%I:%M%p %Z')

    return formatted_datetime
### END HELPER FUNCTIONS ###

def get_current_odds(
    api_key="663519121b56f7c062ce9c3d3f209ec3",#"8c06ffa6d251c1dcbcd1da82b880d452",
    markets="h2h,spreads,totals",
    regions="us,us2",
    odds_format="decimal",
    bookmakers="betonlineag,betmgm,betrivers,betus,bovada,draftkings,fanduel,lowvig,pointsbetus,superbook,unibet_us,williamhill_us,wynnbet,ballybet,espnbet,hardrockbet,sisportsbook,tipico_us,windcreek",
    sports=[
        #"americanfootball_nfl",
        "icehockey_nhl",
        #"americanfootball_ncaaf",
        "baseball_mlb",
        #"soccer_epl",
        #"americanfootball_nfl"
        "basketball_nba",
        #"basketball_ncaab",
        #"baseball_ncaa",
        #"icehockey_nhl"
    ]

):
    res = []
    
    # HARD OVERRIVES!!!!!!!
    #bookmakers="fanduel,betmgm,espnbet"
    markets="h2h"
    sports = [
        #"icehockey_nhl",
        #"americanfootball_ncaaf",
        #"baseball_mlb",
        #"soccer_epl",
        "americanfootball_nfl",
        "basketball_nba",
        #"basketball_ncaab",
        #"baseball_ncaa",
        "icehockey_nhl"
    ]

    for sport in sports:
        request_url = (
            f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?regions={regions}&oddsFormat={odds_format}&markets={markets}&bookmakers={bookmakers}&apiKey={api_key}"
        )
        api_data = requests.get(request_url)
        res += api_data.json()

    print(f"Usage Limits: {api_data.headers['x-requests-used']} used, {api_data.headers['x-requests-remaining']} remaining")
    return res, api_data.headers



def find_arbs(events, qa_range=(5,25)):
    
    # # Write events to pickle file
    with open('events_snapshot.pkl', 'wb') as pickle_file:
        pickle.dump(events, pickle_file)
    
    arbs_collection = {}

    five_round_value = lambda x: round(x / 5) * 5
    arb_cnt, good_arb_cnt = 0, 0
    #events = response_data.json()

    # Reshape API Output to be More Accessibly Organized
    for event in events:
        if "bookmaker" not in event:
            continue
        for bookie in event["bookmakers"]:
            temp = {}
            for market in bookie["markets"]:
                temp[market["key"]] = market["outcomes"]
            bookie["markets"] = deepcopy(temp)


    for event in events:
        #print("event",event)
        if "bookmaker" not in event:
            continue
        for bookie in event["bookmakers"]:
            #print("bookie",bookie)
            for market in bookie["markets"]:
                #print(bookie["markets"][market])

                if len(bookie["markets"][market]) != 2:
                    #print("WARNING CODE #1167:", len(bookie["markets"][market]))'
                    pass

                for line in bookie["markets"][market]:
                    #print("line",line)
                    pass

                line = bookie["markets"][market][0]

                og_line = deepcopy(line)

                side1_price = line["price"]
                point = None
                if "point" in line:
                    point = line["point"]

                for bookie2 in event["bookmakers"]:
                    if bookie["key"] == bookie2["key"] or not (market in bookie2["markets"]):
                        continue

                    #print(bookie2["markets"])
                    line2 = bookie2["markets"][market][1]

                    og_line2 = deepcopy(line2)

                    side2_price = line2["price"]

                    point2 = None
                    if "point" in line2:
                        point2 = line2["point"]

                        if market == "spreads":
                            point2 *= -1

                    if point != point2:
                        #print("WARNING CODE 4550, Points Do Not Match", point, point2)
                        continue

                    #print(line," : ", line2)

                    if arbable(side1_price, side2_price):
                        #print(line," : ", line2)
                        arb_cnt += 1
                        stks = balance_stakes(side1_price, side2_price)
                        guaranteed = round(outcomes(side1_price, side2_price, stks[0], stks[1])[0],2)


                        if guaranteed>qa_range[0] and guaranteed<qa_range[1]:
                            good_arb_cnt += 1


                            rounded = outcomes(side1_price, side2_price, round(stks[0]), round(stks[1]))
                            rounded = tuple(map(lambda x: round(x, 2), rounded))

                            five_rounded = outcomes(side1_price, side2_price, five_round_value(stks[0]), five_round_value(stks[1]))
                            five_rounded = tuple(map(lambda x: round(x, 2), five_rounded))




                            if not event["sport_title"] in arbs_collection:
                                arbs_collection[event["sport_title"]] = {}

                            if not event["id"] in arbs_collection[event["sport_title"]]:
                                arbs_collection[event["sport_title"]][event["id"]] = {
                                    "commence_date": event["commence_time"],
                                    "team1": event["home_team"],
                                    "team2": event["away_team"],
                                    "arbs": []
                                }

                            arbs_collection[event["sport_title"]][event["id"]]["arbs"].append(
                                {
                                    "market": market,
                                    "line1":{
                                        "book": bookie['key'],
                                        "points": point,
                                        "price": dec_to_amer_odds(og_line["price"])
                                    },
                                    "line2":{
                                        "book": bookie2['key'],
                                        "points": point2,
                                        "price": dec_to_amer_odds(og_line2["price"])
                                    },
                                    "fulcrum":{
                                        0:stks,
                                        1:(round(stks[0]),round(stks[1])),
                                        5:(five_round_value(stks[0]),five_round_value(stks[1]))
                                    },
                                    "outcomes":{
                                        0:guaranteed,
                                        1:rounded,
                                        5:five_rounded
                                    }
                                }
                            )


                            #line["price"] = dec_to_amer_odds(og_line["price"])
                            #line2["price"] = dec_to_amer_odds(og_line2["price"])

                            #print(f"{bookie['key']}:{printline(line)} vs {bookie2['key']}:{printline(line2)}")
                            #print(f"\tGuaranteed: +${guaranteed} on $100 bet via {stks} splits")
                            #print(f"\t\t+${rounded} on $100 bet via rounded splits ({round(stks[0])}, {round(stks[1])})")
                            #print(f"\t\t+${five_rounded} on $100 bet via five-rounded splits ({five_round_value(stks[0])}, {five_round_value(stks[1])})")

    # TODO Format Return instead of just printing this shit
    # TODO Break this up in to parse and arb-finding, perhaps
    # TODO validation that home/away are always listed in the same order
    return (arbs_collection, arb_cnt, good_arb_cnt)


def risk_free_range(odds1, odds2, bankroll_max=100):

    outcome1_np = np.zeros([bankroll_max,bankroll_max])
    outcome2_np = deepcopy(outcome1_np)
    entry_cost_np = deepcopy(outcome1_np)
    reward_view = deepcopy(outcome1_np).astype(str)

    for i in range(1,len(outcome1_np)):
        for j in range(1,len(outcome1_np)):
            entry_cost = i + j
            entry_cost_np[i][j] = entry_cost
            reward_view[i][j] = -1
            if(entry_cost <= bankroll_max):
                outcome1_np[i][j] = (odds1*i - entry_cost)/entry_cost
                outcome2_np[i][j] = (odds2*j - entry_cost)/entry_cost
                #print(i,j,outcome1_np[i][j],outcome2_np[i][j])
                if outcome1_np[i][j] >= 0 and outcome2_np[i][j] >= 0:
                    print(f"Risk Free!: {i},{j}: [{outcome1_np[i][j]}, {outcome2_np[i][j]}]")
                    reward_view[i][j] = str(outcome1_np[i][j]) + "," + str(outcome2_np[i][j])

            else:
                outcome1_np[i][j] = -1
                outcome2_np[i][j] = -1

    return reward_view

#### Sample Usage ###
#risk_free_range(1.22,9.5)

### Pickle Functions ###

def save_data(target_data, filename):
    with open("pickle_jar/"+filename+'.pkl', 'wb') as f:
        pickle.dump(target_data, f)
    f.close()

def load_data(filename):
    data = None
    with open("pickle_jar/"+filename, 'rb') as f:
        data = pickle.load(f)
    f.close()
    return data

def arbs_to_df(data):
    df = pd.DataFrame(columns=['sport', 'event-id', 'date', 'team1', 'team2', 'book1', 'book2', 'market', 'points1', 'points2', 'price1', 'price2', 'value', 'fulcrum', 'outcomes'])

    for sport in data:
        for event in data[sport]:
            date = data[sport][event]["commence_date"]
            team1 = data[sport][event]["team1"]
            team2 = data[sport][event]["team2"]
            for arb in data[sport][event]["arbs"]:
                book1 = arb["line1"]["book"]
                points1 = arb["line1"]["points"]
                price1 = arb["line1"]["price"]

                book2 = arb["line2"]["book"]
                points2 = arb["line2"]["points"]
                price2 = arb["line2"]["price"]

                value = arb["outcomes"][0]
                fulcrum = arb["fulcrum"]
                outcomes = arb["outcomes"]
                market = arb["market"]

                new_row = [sport, event, date, team1, team2, book1, book2, market, points1, points2, price1, price2, value, fulcrum, outcomes]
                df.loc[len(df)] = new_row
    return df


@app.route('/get_arbs_html', methods = ['POST'])
@cross_origin()
def get_arbs_html():
    input_str = request.form['prompt']
    reload = False
    if input_str  == "true":
        reload = True

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if reload:
        print("Fresh data requested, hitting API!")
        API_data = get_current_odds()
        save_data(API_data, "api_data_"+timestamp)
        print(f"Usage Limits: {API_data[1]['x-requests-used']} used, {API_data[1]['x-requests-remaining']} remaining")
    else:
        directory = "pickle_jar"
        files = os.listdir(directory)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
        most_recent_file = files[0]
        # Optional Override
        #most_recent_file = "test71.pkl"
        print("Using: " + most_recent_file)
        API_data = load_data(most_recent_file)

    if type(API_data) == tuple:
        print("was tuple")
        headers = API_data[1]
        API_data = API_data[0]
    else:
        print("was not tuple")
        headers = API_data.headers
        API_data = API_data.json()

    arbs = find_arbs(API_data, qa_range=(2,25))
    print(arbs[1],arbs[2])
    df = arbs_to_df(arbs[0]).sort_values("value", ascending=False)

    df["Matchup"] = df["team1"]+"\n"+df["team2"]


    df["price1"] = df["price1"].apply(lambda x: "+" + str(x) if x>0 else str(x))
    df["price2"] = df["price2"].apply(lambda x: "+" + str(x) if x>0 else str(x))

    df['Bet'] = df['market'].replace('h2h', 'Moneyline')
    #df["points1"] = df["points1"].apply(lambda x: "+" + str(x) if (x!=None and x>0) else x)
    df["points1"] = df.apply(lambda row: '+' + str(row['points1']) if row['market'] == "spreads" and row['points1'] > 0 else row['points1'], axis=1)

    df['Bet'] = df.apply(lambda row: "Spread\n" + str(row['team1'].split(" ")[-1] ) + " " + str(row['points1'])  if row['Bet'] == "spreads" else row['Bet'], axis=1)
    df['Bet'] = df.apply(lambda row: "Over " + str(row['points1'])  + "\nUnder " + str(row['points1'])  if row['Bet'] == "totals" else row['Bet'], axis=1)

    df["Arbitrage Lines"] = df["book1"] + " @ " + df["price1"] + "\n" + df["book2"] + " @ " + df["price2"]


    df = df.drop(["event-id", "team1", "team2", "book1", "book2", "price1", "price2", 'points1', 'points2'], axis=1)

    df["Game Time"] = df["date"].apply(convert_to_eastern_time)
    df["Value"] = df["value"].astype(str) + "%"

    def test_fn(d,key):
        return tuple(map(lambda x: str(round(x, 2))+"%", d[key]))

    df["Fulcrum Stake Split"] = df["fulcrum"].apply(lambda x: test_fn(x, 0)[0] + "LINEBREAK" + test_fn(x, 0)[1])
    df["1-RoundedLINEBREAK(Split => Outcomes)"] = df["fulcrum"].apply(lambda x: test_fn(x, 1)[0] +", "+test_fn(x, 1)[1]) +  " =>\n" + df["outcomes"].apply(lambda x: str(test_fn(x, 1)[0] + ", " + test_fn(x, 1)[1]))
    df["5-RoundedLINEBREAK(Split => Outcomes)"] = df["fulcrum"].apply(lambda x: test_fn(x, 5)[0] +", "+test_fn(x, 5)[1]) +  " =>\n" + df["outcomes"].apply(lambda x: str(test_fn(x, 5)[0] + ", " + test_fn(x, 5)[1]))
    df["Sport"]=df["sport"]

    df2 = df[["Game Time","Sport",'Matchup','Bet','Arbitrage Lines','Value','Fulcrum Stake Split',"1-RoundedLINEBREAK(Split => Outcomes)","5-RoundedLINEBREAK(Split => Outcomes)"]]#,'fulcrum','outcomes']]

    out = df2.to_html(index=False).replace("\\n","<br/>").replace("LINEBREAK","<br/>").split("<table border=\"1\" class=\"dataframe\">\n  ")[1]

    input_date = headers["Date"]
    dt = datetime.strptime(input_date, '%a, %d %b %Y %H:%M:%S %Z')
    gmt = pytz.timezone('GMT')
    est = dt.astimezone(pytz.timezone('EST'))
    est_string = est.strftime('%Y-%m-%d %H:%M:%S %Z')

    return (jsonify({'x': est_string, 'y':headers['x-requests-used'], 'z':headers['x-requests-remaining'], 'html': out}))#(orient="records"))

# TODO: Revisit to conflate this above.
@app.route('/get_arbs_df', methods = ['POST'])
@cross_origin()
def get_arbs_df():
    try:
        input_str = request.form['prompt']
    except:
        input_str = False

    reload = False
    if input_str  == "true" or input_str  == "True" :
        reload = True

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if reload:
        print("Fresh data requested, hitting API!")
        API_data = get_current_odds(regions="us2,us", bookmakers="espnbet, fanduel", markets="h2h",
            sports=[
                "basketball_nba",
                "basketball_ncaab",
                "icehockey_nhl",
                "soccer_epl",
                "americanfootball_nfl"
            ]
        )
        save_data(API_data, "api_data_"+timestamp)
        print(f"Usage Limits: {API_data[1]['x-requests-used']} used, {API_data[1]['x-requests-remaining']} remaining")
    else:
        directory = "pickle_jar"
        files = os.listdir(directory)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
        most_recent_file = files[0]
        # Optional Override
        #most_recent_file = "test71.pkl"
        print("Using: " + most_recent_file)
        API_data = load_data(most_recent_file)

    if type(API_data) == tuple:
        print("was tuple")
        headers = API_data[1]
        API_data = API_data[0]
    else:
        print("was not tuple")
        headers = API_data.headers
        API_data = API_data.json()

    arbs = find_arbs(API_data, qa_range=(2,25))
    print(arbs[1],arbs[2])
    df = arbs_to_df(arbs[0]).sort_values("value", ascending=False)

    df["Matchup"] = df["team1"]+"\n"+df["team2"]


    df["price1"] = df["price1"].apply(lambda x: "+" + str(x) if x>0 else str(x))
    df["price2"] = df["price2"].apply(lambda x: "+" + str(x) if x>0 else str(x))

    df['Bet'] = df['market'].replace('h2h', 'Moneyline')
    #df["points1"] = df["points1"].apply(lambda x: "+" + str(x) if (x!=None and x>0) else x)
    df["points1"] = df.apply(lambda row: '+' + str(row['points1']) if row['market'] == "spreads" and row['points1'] > 0 else row['points1'], axis=1)

    df['Bet'] = df.apply(lambda row: "Spread\n" + str(row['team1'].split(" ")[-1] ) + " " + str(row['points1'])  if row['Bet'] == "spreads" else row['Bet'], axis=1)
    df['Bet'] = df.apply(lambda row: "Over " + str(row['points1'])  + "\nUnder " + str(row['points1'])  if row['Bet'] == "totals" else row['Bet'], axis=1)

    df["Arbitrage Lines"] = df["book1"] + " @ " + df["price1"] + "\n" + df["book2"] + " @ " + df["price2"]


    df = df.drop(["event-id", "team1", "team2", "book1", "book2", "price1", "price2", 'points1', 'points2'], axis=1)

    df["Game Time"] = df["date"].apply(convert_to_eastern_time)
    df["Value"] = df["value"].astype(str) + "%"

    def test_fn(d,key):
        return tuple(map(lambda x: str(round(x, 2))+"%", d[key]))

    df["Fulcrum Stake Split"] = df["fulcrum"].apply(lambda x: test_fn(x, 0)[0] + "LINEBREAK" + test_fn(x, 0)[1])
    df["1-RoundedLINEBREAK(Split => Outcomes)"] = df["fulcrum"].apply(lambda x: test_fn(x, 1)[0] +", "+test_fn(x, 1)[1]) +  " =>\n" + df["outcomes"].apply(lambda x: str(test_fn(x, 1)[0] + ", " + test_fn(x, 1)[1]))
    df["5-RoundedLINEBREAK(Split => Outcomes)"] = df["fulcrum"].apply(lambda x: test_fn(x, 5)[0] +", "+test_fn(x, 5)[1]) +  " =>\n" + df["outcomes"].apply(lambda x: str(test_fn(x, 5)[0] + ", " + test_fn(x, 5)[1]))
    df["Sport"]=df["sport"]

    df2 = df[["Game Time","Sport",'Matchup','Bet','Arbitrage Lines','Value','Fulcrum Stake Split',"1-RoundedLINEBREAK(Split => Outcomes)","5-RoundedLINEBREAK(Split => Outcomes)"]]#,'fulcrum','outcomes']]

    # TODO: For above comment, the only change I think is gonna be commenting this line out?
    # out = df2.to_html(index=False).replace("\\n","<br/>").replace("LINEBREAK","<br/>").split("<table border=\"1\" class=\"dataframe\">\n  ")[1]

    input_date = headers["Date"]
    dt = datetime.strptime(input_date, '%a, %d %b %Y %H:%M:%S %Z')
    gmt = pytz.timezone('GMT')
    est = dt.astimezone(pytz.timezone('EST'))
    est_string = est.strftime('%Y-%m-%d %H:%M:%S %Z')

    return (jsonify({'x': est_string, 'y':headers['x-requests-used'], 'z':headers['x-requests-remaining'], 'dataframe': df2.to_json()}))#(orient="records"))

