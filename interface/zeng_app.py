from flask import Flask, render_template, request, jsonify, send_from_directory, current_app, Request
import os
import json


## fields
movies_fields = ['Title', 'US_Gross', 'Worldwide_Gross', 'US_DVD_Sales', 'Production_Budget', 'Release_Date',
                 'MPAA_Rating', 'Running_Time_min', 'Distributor', 'Source', 'Major_Genre', 'Creative_Type', 'Director',
                 'Rotten_Tomatoes_Rating', 'IMDB_Rating', 'IMDB_Votes']

bs_fields = ['Airport_Name', 'Aircraft_Make_Model', 'Effect_Amount_of_damage', 'Flight_Date',
             'Aircraft_Airline_Operator', 'Origin_State', 'When_Phase_of_flight', 'Wildlife_Size', 'Wildlife_Species',
             'When_Time_of_day', 'Cost_Other', 'Cost_Repair', 'Cost_Total', 'Speed_IAS_in_knots']

cars_fields = ["Cylinders", "Name", "Origin", "Year", "Acceleration", "Displacement", "Horsepower", "Miles_per_Gallon",
               "Weight_in_lbs"]

## read dataset:
## demo - car
read_cars_flds_to_vglstr = open('./data/cars/fields_to_vglstr.json', 'r')
cars_flds_to_vglstr = json.load(read_cars_flds_to_vglstr)

read_cars_results = open('./data/cars/results.json', 'r')
cars_results = json.load(read_cars_results)

## movies
## dziban
read_movies_diban_flds_to_vglstr = open('./data/movies/dziban_fields_to_vglstr.json', 'r')
movies_dziban_flds_to_vglstr = json.load(read_movies_diban_flds_to_vglstr)

read_movies_dziban_bfs_results = open('./data/movies/dziban_bfs_results.json', 'r')
movies_dziban_bfs_results = json.load(read_movies_dziban_bfs_results)

read_movies_dziban_dfs_results = open('./data/movies/dziban_dfs_results.json', 'r')
movies_dziban_dfs_results = json.load(read_movies_dziban_dfs_results)

## cql
read_movies_cql_flds_to_vglstr = open('./data/movies/cql_fields_to_vglstr.json', 'r')
movies_cql_flds_to_vglstr = json.load(read_movies_cql_flds_to_vglstr)

read_movies_cql_bfs_results = open('./data/movies/cql_bfs_results.json', 'r')
movies_cql_bfs_results = json.load(read_movies_cql_bfs_results)

read_movies_cql_dfs_results = open('./data/movies/cql_dfs_results.json', 'r')
movies_cql_dfs_results = json.load(read_movies_cql_dfs_results)

## birdstrikes
## dziban
read_bs_dizban_flds_to_vglstr = open('./data/birdstrikes/dziban_fields_to_vglstr.json', 'r')
bs_dziban_flds_to_vglstr = json.load(read_bs_dizban_flds_to_vglstr)

read_bs_dziban_bfs_results = open('./data/birdstrikes/dziban_bfs_results.json', 'r')
bs_dziban_bfs_results = json.load(read_bs_dziban_bfs_results)

read_bs_dziban_dfs_results = open('./data/birdstrikes/dziban_dfs_results.json', 'r')
bs_dziban_dfs_results = json.load(read_bs_dziban_dfs_results)

## cql
read_bs_cql_flds_to_vglstr = open('./data/birdstrikes/cql_fields_to_vglstr.json', 'r')
bs_cql_flds_to_vglstr = json.load(read_bs_cql_flds_to_vglstr)

read_bs_cql_bfs_results = open('./data/birdstrikes/cql_bfs_results.json', 'r')
bs_cql_bfs_results = json.load(read_bs_cql_bfs_results)

read_bs_cql_dfs_results = open('./data/birdstrikes/cql_dfs_results.json', 'r')
bs_cql_dfs_results = json.load(read_bs_cql_dfs_results)


## communicate with demo

def demo_snd_flds():
    received_data = json.loads(request.form.get('data'))
    fields = received_data["fields"]

    # init:
    if len(fields) == 0:
        initCharts = []
        for fld in cars_fields:
            temp = {}
            vstr = cars_flds_to_vglstr[fld]
            temp[vstr] = get_vgl_from_vglstr(vstr, "cars")
            initCharts.append(temp)
        return jsonify(status="success", recVegalite=initCharts)

    # if empty chart:
    fields.sort()
    fields_str = "+".join(fields)
    if cars_flds_to_vglstr[fields_str] == "":
        return jsonify(status="empty")

    # if not empty chart:
    actual_vgl = {}
    vglstr = cars_flds_to_vglstr[fields_str]
    actual_vgl[vglstr] = get_vgl_from_vglstr(vglstr, "cars")
    # get recomendation:
    rec_vgl = cars_results[vglstr]
    # print (bfs_vl)
    rec_ranked = sorted(rec_vgl, key=rec_vgl.get)
    # print (bfsRanked)
    rec_ranked_final = []
    for vstr in rec_ranked:
        temp = {}
        temp[vstr] = get_vgl_from_vglstr(vstr, "cars")
        rec_ranked_final.append(temp)
    return jsonify(status="success", actualVegalite=actual_vgl, recVegalite=rec_ranked_final)


def demo_snd_spcs():
    received_data = json.loads(request.form.get('data'))
    vgl = received_data["vgl"]
    vglstr = get_vglstr_from_vgl(vgl)

    if vglstr in cars_results:
        print("bfs vglstr exists.")
        rec_vgl = cars_results[vglstr]
    else:
        print("bfs vglstr does not exist.")
        fields = get_fields_from_vglstr(vglstr)
        new_vglstr = cars_flds_to_vglstr["+".join(fields)]
        rec_vgl = cars_results[new_vglstr]

    rec_ranked = sorted(rec_vgl, key=rec_vgl.get)
    rec_ranked_final = []

    for vstr in rec_ranked:
        temp = {}
        temp[vstr] = get_vgl_from_vglstr(vstr, "cars")
        rec_ranked_final.append(temp)

    return jsonify(status="success", recVegalite=rec_ranked_final)



def perform_snd_flds(request):
    received_data = json.loads(request.get('data'))
    fields = received_data["fields"]
    version = received_data["version"]
    print(version)

    cur_fields = []
    cur_flds_to_vglstr = {}
    cur_results = {}
    cur_dataset = ""

    if version[0] == "a":
        cur_fields = movies_fields
        cur_dataset = "movies"
        if version[1] == "d":
            cur_flds_to_vglstr = movies_dziban_flds_to_vglstr
            if version[2] == "e":
                cur_results = movies_dziban_bfs_results
            elif version[2] == "f":
                cur_results = movies_dziban_dfs_results
        elif version[1] == "c":
            cur_flds_to_vglstr = movies_cql_flds_to_vglstr
            if version[2] == "e":
                cur_results = movies_cql_bfs_results
            elif version[2] == "f":
                cur_results = movies_cql_dfs_results
    elif version[0] == "b":
        cur_fields = bs_fields
        cur_dataset = "birdstrikes"
        if version[1] == "d":
            cur_flds_to_vglstr = bs_dziban_flds_to_vglstr
            if version[2] == "e":
                cur_results = bs_dziban_bfs_results
            elif version[2] == "f":
                cur_results = bs_dziban_dfs_results
        elif version[1] == "c":
            cur_flds_to_vglstr = bs_cql_flds_to_vglstr
            if version[2] == "e":
                cur_results = bs_cql_bfs_results
            elif version[2] == "f":
                cur_results = bs_cql_dfs_results

    # init:
    if len(fields) == 0:
        initCharts = []
        for fld in cur_fields:
            temp = {}
            vstr = cur_flds_to_vglstr[fld]
            temp[vstr] = get_vgl_from_vglstr(vstr, cur_dataset)
            initCharts.append(temp)
        return jsonify(status="success", recVegalite=initCharts)

    # if empty chart:
    fields.sort()
    fields_str = "+".join(fields)
    if cur_flds_to_vglstr[fields_str] == "":
        return jsonify(status="empty")

    # if not empty chart:
    actual_vgl = {}
    vglstr = cur_flds_to_vglstr[fields_str]
    actual_vgl[vglstr] = get_vgl_from_vglstr(vglstr, cur_dataset)
    ## if dziban:
    if version[1] == "d":
        rec_vgl = cur_results[vglstr]

    elif version[1] == "c":
        rec_vgl = cur_results[fields_str]

    rec_ranked = sorted(rec_vgl, key=rec_vgl.get)
    if len(rec_ranked) > 25:
        rec_ranked = rec_ranked[:25]
    rec_ranked_final = []
    for vstr in rec_ranked:
        temp = {}
        temp[vstr] = get_vgl_from_vglstr(vstr, cur_dataset)
        rec_ranked_final.append(temp)

    return actual_vgl, rec_ranked_final



def perform_snd_spcs(request):
    received_data = json.loads(request.form.get('data'))
    vgl = received_data["vgl"]
    version = received_data["version"]
    vglstr = get_vglstr_from_vgl(vgl)

    cur_fields = []
    cur_flds_to_vglstr = {}
    cur_results = {}
    cur_dataset = ""

    if version[0] == "a":
        cur_fields = movies_fields
        cur_dataset = "movies"
        if version[1] == "d":
            cur_flds_to_vglstr = movies_dziban_flds_to_vglstr
            if version[2] == "e":
                cur_results = movies_dziban_bfs_results
            elif version[2] == "f":
                cur_results = movies_dziban_dfs_results
        elif version[1] == "c":
            cur_flds_to_vglstr = movies_cql_flds_to_vglstr
            if version[2] == "e":
                cur_results = movies_cql_bfs_results
            elif version[2] == "f":
                cur_results = movies_cql_dfs_results
    elif version[0] == "b":
        cur_fields = bs_fields
        cur_dataset = "birdstrikes"
        if version[1] == "d":
            cur_flds_to_vglstr = bs_dziban_flds_to_vglstr
            if version[2] == "e":
                cur_results = bs_dziban_bfs_results
            elif version[2] == "f":
                cur_results = bs_dziban_dfs_results
        elif version[1] == "c":
            cur_flds_to_vglstr = bs_cql_flds_to_vglstr
            if version[2] == "e":
                cur_results = bs_cql_bfs_results
            elif version[2] == "f":
                cur_results = bs_cql_dfs_results

    if version[1] == "d":
        if vglstr in cur_results:
            print("vglstr exists.")
            rec_vgl = cur_results[vglstr]
        else:
            print("vglstr does not exist.")
            fields = get_fields_from_vglstr(vglstr)
            new_vglstr = cur_flds_to_vglstr["+".join(fields)]
            rec_vgl = cur_results[new_vglstr]

    elif version[1] == "c":
        fields = get_fields_from_vglstr(vglstr)
        fields_str = "+".join(fields)
        rec_vgl = cur_results[fields_str]

    rec_ranked = sorted(rec_vgl, key=rec_vgl.get)
    if len(rec_ranked) > 25:
        rec_ranked = rec_ranked[:25]
    rec_ranked_final = []

    for vstr in rec_ranked:
        temp = {}
        temp[vstr] = get_vgl_from_vglstr(vstr, cur_dataset)
        rec_ranked_final.append(temp)

    return jsonify(status="success", recVegalite=rec_ranked_final)


## get username-version:

def snd_user_info():
    received_data = json.loads(request.form.get('data'))
    username = received_data["username"]
    status = received_data["status"]
    if status == "pilot":
        read_pu = open("pilot_user_info.json", "r")
        pu = json.load(read_pu)
        if username in pu:
            return jsonify(status="invalid")
        else:
            pu.append(username)
            with open("pilot_user_info.json", "w") as out:
                json.dump(pu, out)
            return jsonify(status="success", username=username, version="pilot")
    elif status == "study":
        read_su = open('study_user_info.json', 'r')
        su = json.load(read_su)
        if username in su:
            new_uname = su[username]["username"]
            version = su[username]["version"]
            return jsonify(status="success", username=new_uname, version=version)
        else:
            return jsonify(status="invalid")


## get study interaction log:

def snd_demo_interaction_logs():
    received_data = json.loads(request.form.get('log'))
    interaction_logs = received_data["interactionLogs"]
    status = received_data["status"]
    username = received_data["username"]
    interface = received_data["interface"]
    bookmarked = received_data["bookmarked"]

    with open('./logs/' + status + '/' + username + '_' + interface + '_logs.json', 'w') as out:
        json.dump(interaction_logs, out, indent=2)

    with open('./logs/' + status + '/' + username + '_' + interface + '_bookmarked.json', 'w') as out:
        json.dump(bookmarked, out, indent=2)

    return jsonify(status="success")


## get study interaction log:

def snd_interaction_logs():
    received_data = json.loads(request.form.get('data'))
    interaction_logs = received_data["interactionLogs"]
    status = received_data["status"]
    username = received_data["username"]
    version = received_data["version"]
    interface = received_data["interface"]
    bookmarked = received_data["bookmarked"]
    answer = received_data["answer"]
    pt_ans = received_data["ptaskAns"]

    with open('./logs/' + status + '/' + username + '_' + version + '_' + interface + '_logs.json', 'w') as out:
        json.dump(interaction_logs, out, indent=2)

    with open('./logs/' + status + '/' + username + '_' + version + '_' + interface + '_bookmarked.json', 'w') as out:
        json.dump(bookmarked, out, indent=2)

    with open('./logs/' + status + '/' + username + '_' + version + '_' + interface + '_answer.json', "w") as out:
        json.dump({"answer": answer}, out, indent=2)

    with open('./logs/' + status + '/' + username + '_' + version + '_' + interface + '_ptask.json', "w") as out:
        json.dump(pt_ans, out, indent=2)

    return jsonify(status="success")



def ptsk_snd_ans():
    received_data = json.loads(request.form.get('data'))
    questAns = received_data["questAns"]
    status = received_data["status"]
    username = received_data["username"]
    version = received_data["version"]
    interface = received_data["interface"]

    with open('./logs/' + status + '/' + username + '_' + version + '_' + interface + '.json', 'w') as out:
        json.dump(questAns, out, indent=2)

    if status == "study" and interface == "intv":
        read_su = open('study_user_info.json', 'r')
        su = json.load(read_su)
        for email in su:
            if su[email]["username"] == username:
                return jsonify(status="success", code=su[email]["complete-code"])

    return jsonify(status="success")


# helper methods:
def get_vglstr_from_vgl(vgl):
    vglstr = ""
    vglstr += "mark:" + vgl["mark"] + ';'
    encoding_arr = []
    for encoding in vgl["encoding"]:
        if encoding == "undefined":
            continue
        encoding_str = ""
        if "field" in vgl["encoding"][encoding]:
            encoding_str += vgl["encoding"][encoding]["field"] + "-"
        else:
            encoding_str += "-"
        encoding_str += vgl["encoding"][encoding]["type"] + "-"
        encoding_str += encoding
        if "aggregate" in vgl["encoding"][encoding]:
            encoding_str += "<" + "aggregate" + ">" + vgl["encoding"][encoding]["aggregate"]
        if "bin" in vgl["encoding"][encoding]:
            encoding_str += "<" + "bin" + ">"

        encoding_arr.append(encoding_str)

    encoding_arr.sort()
    vglstr += "encoding:" + ",".join(encoding_arr)

    return vglstr


def get_vgl_from_vglstr(vglstr, dataset):
    vgl = {}
    vgl["$schema"] = "https://vega.github.io/schema/vega-lite/v3.json"
    # vgl["data"] = {"url": "data/movies.json"}
    vgl["data"] = {"url": "/data/" + dataset + "/" + dataset + ".json"}
    mark = vglstr.split(';')[0]
    encoding = vglstr.split(';')[1]
    vgl["mark"] = mark.split(':')[1]
    encodings = {}
    fields = []
    encoding = encoding.split(':')[1]
    encoding_arr = encoding.split(',')
    for encode in encoding_arr:
        one_encoding = {}
        if '<' in encode:
            regular = encode.split('<')[0]
            transform = encode.split('<')[1]

            regular_split = regular.split('-')
            if len(regular_split) != 3:
                print("something wrong with regular string.")
            field = regular_split[0]
            attr_type = regular_split[1]
            encoding_type = regular_split[2]

            one_encoding["type"] = attr_type
            if field != '':
                one_encoding["field"] = field
                fields.append(field)

            transform_split = transform.split('>')
            transform_type = transform_split[0]
            transform_val = transform_split[1]

            if transform_type == "bin":
                one_encoding["bin"] = True
            else:
                one_encoding[transform_type] = transform_val

            # encodings[encoding_type] = one_encoding

        else:
            encode_split = encode.split('-')
            if len(encode_split) != 3:
                print("something wrong with encode string.")

            field = encode_split[0]
            attr_type = encode_split[1]
            encoding_type = encode_split[2]

            one_encoding["type"] = attr_type
            if field != '':
                one_encoding["field"] = field
                fields.append(field)
            else:
                print("something wrong:")
                print(vglstr)

            ## for bs Flight_Date
            if encode == "Flight_Date-nominal-row":
                if "-x" not in vglstr:
                    encoding_type = "x"
                elif "-y" not in vglstr:
                    encoding_type = "y"
                elif "-color" not in vglstr:
                    encoding_type = "color"
                else:
                    encoding_type = "size"

            if "Flight_Date-nominal" in encode:
                one_encoding["timeUnit"] = "month"

            ## for movie Release_Date
            if encode == "Release_Date-nominal-row":
                if "-x" not in vglstr:
                    encoding_type = "x"
                elif "-y" not in vglstr:
                    encoding_type = "y"
                elif "-color" not in vglstr:
                    encoding_type = "color"
                else:
                    encoding_type = "size"

            if "Release_Date-nominal" in encode:
                one_encoding["timeUnit"] = "month"

        if "field" in one_encoding:
            if one_encoding["field"] == "Title":
                if encoding_type == "x":
                    vgl["width"] = 3200
                else:
                    vgl["height"] = 18000
            if one_encoding["field"] == "Director" or one_encoding["field"] == "Distributor":
                if encoding_type == "x":
                    vgl["width"] = 3200

        encodings[encoding_type] = one_encoding

    vgl["encoding"] = encodings
    return vgl


def get_fields_from_vglstr(vglstr):
    encoding_str = vglstr.split(';')[1]
    encoding_str = encoding_str.split(':')[1]
    encodings = encoding_str.split(',')
    fields = []
    for encode in encodings:
        field = encode.split('-')[0]
        if field == '':
            continue
        fields.append(field)
    fields.sort()
    return fields


if __name__ == '__main__':
    # Simulate the request data
    request_data = {
        "data": json.dumps({
            "fields": ['Aircraft_Make_Model', 'Airport_Name'],
            "version": "bdf"
        })
    }

    # Create a mock request object
    mock_request = Request(request_data)

    # Call the function with the mock request
    result = perform_snd_flds(request_data)
    print(result)
