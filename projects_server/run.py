from flask import Flask, render_template, request, redirect, session
from problem import Problem
from datetime import datetime
import os
import json 

problemPath = 'static/project_rsc/proj1_v2.json'
directory = "results"
problems = Problem.factoryFromJson(problemPath)

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

def testLogin(name, emp_id):
    if len(name) == 0:
        session['logged_in'] = False 
        return "/login" 
    #TODO, check name to login
    else:
        session['logged_in'] = True 
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
    if not ("logged_in" in session):
        return redirect('/login')
    if not session["logged_in"]:
        return redirect('/login')

    result = ""
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8899', debug=True)
