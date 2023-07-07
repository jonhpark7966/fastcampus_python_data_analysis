from flask import send_file
import json 

class Problem:
    question = ""
    inputValue = None
    answerValue = []
    isCorrect = None 

    # construct all problems
    @staticmethod
    def factoryFromJson(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            jsonData = json.load(f)
            problems = []
            for problem in jsonData['problems']:
                problems.append( Problem.fromJson(problem))
            return problems

        assert(False)

    # construct "a" problem
    @staticmethod
    def fromJson(jsonObject):
        if jsonObject['answer']['type'] == "value":
            return ValueProblem(jsonObject['question'], jsonObject['answer'])
        elif jsonObject['answer']['type'] == "table":
            return TableProblem(jsonObject['question'], jsonObject['answer'])
        elif jsonObject['answer']['type'] == "graph":
            return GraphProblem(jsonObject['question'], jsonObject['answer'])



        assert(False)

    def genView(self):
        assert(False) # interface.

    def setValue(self, formDict):
        return

    def testAnswer(self, input, answer):
        ret = (input == answer)
        if not ret:
            try:
                ret = round(float(input), 1) == round(float(answer),1)
            except:
                ret = False
                print("Parsing ERROR!")
        return ret

    def validTag(self, isValid):
        if isValid is None:
            return ""
        elif isValid:
            return "is-valid"
        else:
            return "is-invalid"
    

class ValueProblem(Problem):
    def __init__(self, question, answer):
        self.question = question
        self.answerValue = answer['value']
        self.inputValue = ""
    
    def genView(self):
        return f"""
        <div class="container">
        <h3>Q. {self.question}</h3>
        <div class="form-group" style="width: 500px;">
            <input type="text" name="{self.question}" value="{self.inputValue}" class="form-control {self.validTag(self.isCorrect)}" aria-describedby="helpInline">
        </div>
        </div>
        """
    def setValue(self, formDict):
        self.inputValue = formDict[self.question]
        self.isCorrect = self.testAnswer(self.inputValue, self.answerValue)
    
    def isAllCorrect(self):
        return self.isCorrect


class TableProblem(Problem):

    def __init__(self, question, answer):
        self.question = question
        self.answerValue = (answer['value'])
        self.inputValue = {}

    def genView(self):
        tableHeader = self.genTableHeader()
        tableBody = self.genTableBody() 

        return f"""
        <div class="container">
        <h3>Q. {self.question}</h3>
        <table class="table">
        {tableHeader}
        {tableBody}
        </table>
    </div>
        """


    def genTableHeader(self):
        ret = ""
        for key in self.answerValue.keys():
            if key == 'index':
                ret += f"<th>---</th>"
            else:
                ret += f"<th>{key}</th>"

        return f"""<thead>
                <tr>{ret}</tr>
            </thead>"""

    def genTableBody(self):
        ret = "<tbody>"
        for value in self.answerValue['index']:
            ret += "<tr>"
            for key in self.answerValue.keys():
                if key == 'index':
                    ret += f'<td>{value}</td>'
                else:
                    name = self.question+'_'+value+'_'+key
                    inputValue = ""
                    if name in self.inputValue:
                        inputValue = self.inputValue[name]

                    if self.isCorrect is None:
                        correct = None
                    elif  name in self.isCorrect:
                        correct = self.isCorrect[name]
                    else:
                        correct = None
                    
                    ret += f'''<td><input type="text"
                     name="{name}"
                     value="{inputValue}"
                     class="form-control {self.validTag(correct)}"></td>'''
            ret+="</tr>"
        ret +="</tbody>"
        return ret

    def setValue(self, formDict):
        if self.isCorrect is None:
            self.isCorrect = {}

        for value in self.answerValue['index']:
            for key in self.answerValue.keys():
                if key != 'index':
                    name=f"{self.question}_{value}_{key}"
                    self.inputValue[name] = formDict[name]
                    answerValue = self.answerValue[key][self.answerValue['index'].index(value)]
                    self.isCorrect[name] = self.testAnswer(self.inputValue[name], answerValue)
    
    def isAllCorrect(self):
        ret = False 
        for value in self.answerValue['index']:
            for key in self.answerValue.keys():
                if key != 'index':
                    name=f"{self.question}_{value}_{key}"
                    if name in self.isCorrect:
                        if not self.isCorrect[name]:
                            return False
                        else:
                            ret = True
        return ret


class GraphProblem(Problem):
    def __init__(self, question, answer):
        self.question = question
        self.answerValue = answer['value']
    
    def genView(self):
        imgs = ""
        for imgPath in self.answerValue:
            imgRelPath = "../static/project_rsc/" + imgPath
            imgs += '<div class="col-md-4"><img src='+ imgRelPath  + '></div>'

        return f"""
        <div class="container">
        <h3>Q. {self.question}</h3>
        <div class="row">
        {imgs}
        </div>
        </div>
        """

    def isAllCorrect(self):
        return True 

                        
                        



# TEST!
if __name__ == '__main__':
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        problems = Problem.factoryFromJson(data)
        print(problems)