from flask import Flask, render_template, request, redirect, session
from problem import Problem
from datetime import datetime
import os
import json 

problemPath = 'static/project_rsc/proj2_v3.json'
directory = "results"
problemsDict = {}

def readNames(path):
    with open(path, 'r', encoding='utf-8') as file:
        # Read the contents of the file
        content = file.read()

    # Split the content by newline and create a list
    ret = content.split('\n')
    return ret

names = readNames('static/names.txt')

app = Flask(__name__)
app.secret_key = 'your_secret_key' 


def saveToFile(resultDict):
    try:
        os.mkdir(directory)
    except FileExistsError:
        print("")

    date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    resultDict['time'] = date_time
    file_path = os.path.join(directory, session['name']) 
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(resultDict, file, ensure_ascii=False)

    print(file,resultDict)

def testLogin(name, emp_id):
    if len(name) == 0:
        session['logged_in'] = False 
        return "/login" 
    elif not name in names:
        session['logged_in'] = False 
        return "/login" 
    else:
        session['logged_in'] = True 
        global problemsDict
        problemsDict[name] = Problem.factoryFromJson(problemPath)
        return "/test" 

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Process the login form data
        session['name'] = request.form['username']
        session['emp_id'] = request.form['password']

        return redirect(testLogin(session['name'], session['emp_id']))
    
    # Render the login form template for GET requests
    return render_template('login.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    try:
        if not ("logged_in" in session):
            return redirect('/login')
        if not session["logged_in"]:
            return redirect('/login')

        result = ""
        global problemsDict
        problems = problemsDict[session['name']]
 
        if request.method == 'POST':
            # form data to problem
            for problem in problems:
                problem.setValue(request.form)

            # save to file
            results = {}
            for problem in problems:
                results[problem.question] = problem.isAllCorrect()

            saveToFile(results)

        return render_template('index.html', problems=problems,
         name=session['name'], emp_id=session['emp_id'])
    except:
        return redirect('/login')



def read_results(directory):
    file_list = os.listdir(directory)

    ret = {}
    for file_name in file_list:
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                file_contents = file.read()
                try:
                    json_data = json.loads(file_contents)
                    ret[file_name] = json_data
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
    return ret

@app.route('/grading')
def grading():
    jsonDict = read_results(directory)
    results = ""
    for name, json in jsonDict.items():
        isAllCorrected = True 
        for key, value in json.items():
            if key != 'time':
                if value == False:
                    isAllCorrected = False
        
        results += f'{name}, {isAllCorrected} <br>'

    return results


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8899', debug=True)
