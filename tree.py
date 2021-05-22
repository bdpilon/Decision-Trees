import pandas as pd
from zipfile import ZipFile, ZIP_DEFLATED
from io import TextIOWrapper
import json
import csv

class ZippedCSVReader:
    def __init__(self, zipped_file):
        unzipped = []
        with ZipFile(zipped_file) as zf:
            for info in zf.infolist():
                name = info.filename
                unzipped.append(name)
            self.paths = sorted(unzipped)
            self.zipped = zipped_file
            
    def load_json(self, file_name):
        #for f in self.paths:
            #if f == file_name:
        with ZipFile(self.zipped) as zf:
            with zf.open(file_name) as f:
                        #tio = TextIOWrapper(f)
                        #data = json.loads(tio.read())
                return json.load(f)#data
    
    def rows(self, file_name = None):
        rows_list = []
        if file_name == None:
            for file in self.paths:
                if file.endswith('.csv'):
                    with ZipFile(self.zipped) as zf:
                        with zf.open(file, "r") as f:
                            tio = TextIOWrapper(f)
                            reader = csv.DictReader(tio)
                            for row in reader:
                                rows_list.append(dict(row))
        else:
            with ZipFile(self.zipped) as zf:
                        with zf.open(file_name, "r") as f:
                            tio = TextIOWrapper(f)
                            reader = csv.DictReader(tio)
                            for row in reader:
                                rows_list.append(dict(row))
        return rows_list
                    
class Loan:
    def __init__(self, amount, purpose, race, income, decision):
        self.amount = amount
        self.purpose = purpose
        self.race = race
        self.income = income
        self.decision = decision
    
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __repr__(self):
        return f"Loan({repr(self.amount)}, {repr(self.purpose)}, {repr(self.race)}, {repr(self.income)}, {repr(self.decision)})"

    def __getitem__(self, lookup):
        try:
            return getattr(self, lookup)
        except:
            if self.amount == lookup or self.purpose == lookup or self.race == lookup or self.income == lookup or self.decision == lookup:
                return 1
            else:
                return 0


class Bank:
    def __init__(self, name, reader):
        self.name = name
        self.reader = reader
        
    def loans(self):
        loans = []
        if self.name == None:
            for row in self.reader.rows():
                if row['action_taken'] == '1':
                    decision = 'approve'
                else: 
                    decision = 'deny' 
                if row['loan_amount_000s']=='':
                    loan_amount = 0
                else:
                    loan_amount = int(row['loan_amount_000s'])
                if row['applicant_income_000s']=='':
                    app_income = 0
                else:
                    app_income = int(row['applicant_income_000s'])
                loans.append(Loan(loan_amount,  row['loan_purpose_name'], row['applicant_race_name_1'], app_income, decision))
            return loans
        else:
            for row in self.reader.rows():
                if row['agency_abbr'] == self.name:
                    if row['action_taken'] == '1':
                        decision = 'approve'
                    else: 
                        decision = 'deny' 
                    if row['loan_amount_000s']=='':
                        loan_amount = 0
                    else:
                        loan_amount = int(row['loan_amount_000s'])
                    if row['applicant_income_000s']=='':
                        app_income = 0
                    else:
                        app_income = int(row['applicant_income_000s'])
                    loans.append(Loan(loan_amount,  row['loan_purpose_name'], row['applicant_race_name_1'], app_income, decision))
            return loans

def get_bank_names(reader):
    bank_list = []
    for row in reader.rows():
        if row['agency_abbr'] in bank_list:
            next
        else:
            bank_list.append(row['agency_abbr'])
    alph_order = sorted(bank_list)
    return alph_order
        
class SimplePredictor():
    def __init__(self):
        self.approved=0
        self.denied = 0

    def predict(self, loan):
        if loan['purpose'] == "Refinancing":
            self.approved+=1
            return True
        else:
            self.denied+=1
            return False

    def get_approved(self):
        return self.approved

    def get_denied(self):
        return self.denied                            
                                 
class DTree(SimplePredictor):
    def __init__(self, nodes):
        super().__init__()
        # a dict with keys: field, threshold, left, right
        # left and right, if set, refer to similar dicts
        self.root = nodes
        self.count = 0
        
    def dump(self, node=None, indent=0):
        self.count += 1
        if node == None:
            node = self.root
        if node["field"] == "class":
            line = "class=" + str(node["threshold"])
        else:
            line = node["field"] + " <= " + str(node["threshold"])
        print("  "*indent + line)
        if node['left']:
            self.dump(node["left"], indent+1)
        if node["right"]:
            self.dump(node["right"], indent+1)
            
            
    def node_count(self, node = None):
        self.count +=1
        if node == None:
            node = self.root
        if node['left']:
            self.node_count(node["left"])
        if node["right"]:
            self.node_count(node["right"])
        return self.count
    
    def predict(self, loan, node = None):
        if node == None:   
            node = self.root
        if node["field"] == "class":
            if node["threshold"] == 0:
                self.denied +=1
                return False
            if node["threshold"] == 1:
                self.approved +=1
                return True 
        if loan[node["field"]]<=node["threshold"]:
            return self.predict(loan, node["left"])
        if loan[node["field"]]>node["threshold"]:
            return self.predict(loan, node["right"])

def bias_test(bank, predictor, race_override):
    biased = 0
    post_list = []
    pre_list = []
    for loan in bank.loans():
        pre_list.append(predictor.predict(loan))
    for loan in bank.loans():
        loan['race'] = race_override
        post_list.append(predictor.predict(loan))
    print(pre_list[1:20])
    print(post_list[1:20])
    assert len(pre_list)==len(post_list)
    for i in range(len(post_list)):
        if pre_list[i] == post_list[i]:
            next
        else:
            biased += 1
    return biased/len(post_list)
    
    


     

        
 
    
