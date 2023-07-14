import csv
import datetime
import pytz
import subprocess
import urllib
import uuid
import requests
import json
import os
from datetime import datetime
from cs50 import SQL
from flask import redirect, render_template, session
from functools import wraps
from freedictionaryapi.clients.sync_client import DictionaryApiClient

# Configure CS50 Library to use SQLite database inside python
usersDb = SQL("sqlite:///users.db")

def login_required(f):

    # Decorate routes to require login.
    # Why do we need to use @wraps decorator: https://www.geeksforgeeks.org/python-functools-wraps-function/
    @wraps(f)

    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#________________Used in Register to create an individual table for the new user's personal categories____________
def create_categories_table(username):
    # Create new table inside users table:
    usersDb.execute(
            "CREATE TABLE ? (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Education TEXT, Housing TEXT, Transportation TEXT, Food TEXT, Utilities TEXT, Insurance TEXT, Medical Healthcare TEXT, SavingInvestingPayments TEXT, PersonalSpending TEXT, RecreationEntertainment TEXT, Miscellaneous TEXT);",
            (username + "_categories"))
    # Adds the default key words from the default_categories_table to the new one:
    usersDb.execute(
            "INSERT INTO ? SELECT id, Education, Housing, Transportation, Food, Utilities, Insurance, MedicalHealthcare, SavingInvestingPayments, PersonalSpending, RecreationEntertainment, Miscellaneous FROM default_categories_table;",
            (username + "_categories"))

# Used the following code to create the default categories table:
def createDefaultTable():
    # Main Budget Categories: https://www.quicken.com/blog/budget-categories/ ;
    # Default Key words:
    # Used https://relatedwords.org/ and https://www.onelook.com/thesaurus/ to get some of the key words that relates to each budget category:
    categories = [{"Education": ['education', 'public', 'university', 'course', 'appliances', 'college', 'polytech', 'student', 'universiti', 'academic', 'academia', 'polytechnical', 'dean', 'polytechnic', 'graduate', 'universitv', 'universites', 'nonuniversity', 'faculty', 'department', 'seminary', 'conservatorium', 'universitie', 'institution', 'dormitory', 'campus', 'undergrad', 'institute', 'provost', 'academy', 'school', 'monash', 'univ', 'postgraduate', 'professor', 'postdoc', 'undergraduate', 'mba', 'studentship', 'doctorate']},
                    {"Housing": ['housing','rent','livingroom', 'village', 'townhome', 'garage', 'bouse', 'outbuilding', 'habitat', 'firm', 'furniture', 'homestead', 'mansion', 'inhabitation', 'cabin', 'woning', 'dwelling-house', 'summerhouse', 'treehouse', 'room', 'workhome', 'houseling', 'refuge', 'houselet', 'house','doghouse', 'chalet', 'housebuilding', 'penthouse', 'bathroom', 'office', 'household', 'put' 'gate', 'office-house', 'attic', 'palace', 'dollhouse', 'townhouse', 'yard', 'apartment', 'courtyard', 'terrace', 'hous', 'residence', 'property', 'habitation', 'home', 'bedroom', 'town', 'shack', 'condo', 'basement', 'manse', 'cabbin', 'sunroom', 'place', 'guesthouse', 'lawn', 'upstairs', 'patio', 'estate', 'street','backyard', 'farmhouse', 'playhouse', 'building', 'garden', 'kitchen', 'neighborhood', 'studio', 'church', 'driveway', 'dwellinghouse', 'shouse']},
                    {"Transportation": ['transload', 'transcytotic', 'convey', 'ferry', 'carry', 'railroad', 'cart',  'gas', 'gasoline', 'alcohol', 'diesel', 'distribution', 'transportation', 'send', 'airlift', 'taxi', 'offloading', 'logistics', 'transhipping', 'destination', 'drive', 'channel', 'transhipment', 'luggage', 'delivery', 'train', 'resupply','transport', 'travel', 'mobility', 'unloading', 'vehicle', 'relocation', 'transporter', 'supply',  'transit', 'transferral', 'shipping', 'airfreight', 'tranship', 'storage', 'export', 'carriage', 'loading', 'transp', 'transshipping', 'translocation', 'ecstasy', 'trucking', 'ride', 'cargo', 'locomotion', 'carrier', 'transmit', 'service', 'rail', 'fuel', 'depot', 'railway', 'transporte']},
                    {"Food": ['dinner', 'food', 'turkey', 'nourishment', 'aliment', 'carbohydrate', 'bread', 'comestible', 'liquor', 'eating', 'cookery', 'grain',  'liver', 'drink', 'gastronomy', 'breadstuff', 'agriculture', 'seafood', 'beer', 'livestock', 'protein', 'buffet', 'sustenance', 'feed', 'eatable', 'dining', 'foodstyle', 'cuisine', 'flesh', 'restaurant', 'sushi', 'gourmet', 'delicacies', 'cereal', 'fish', 'vegetables', 'sometimes', 'solid', 'nutrient', 'pasta', 'fresh', 'drinks', 'snacks', 'dishes', 'diet', 'chicken', 'nutriment', 'fruit', 'meat', 'meal', 'pizza', 'animal', 'daily', 'water', 'foodery', 'groceries', 'helping', 'snack', 'wine', 'dessert', 'milk', 'cooking', 'breakfast', 'nutritious', 'foodstuffs', 'famine']},
                    {"Utilities": ['cables', 'heaters', 'outlets', 'substation', 'providers', 'utilitarian', 'insulators', 'generators', 'electrical', 'essentials', 'utility', 'pipelines', 'efficient', 'resources', 'electrics', 'electric', 'plumbers', 'cable', 'heater', 'ductwork',  'industrials', 'baseload', 'plumbing', 'solar', 'hydroelectricity', 'irrigation', 'terminals', 'supplies', 'installations', 'station', 'heating', 'pipes', 'grid', 'pipework']},
                    {"MedicalHealthcare": [ 'preventible', 'medivac', 'rehabilitatee', 'care', 'oncology', 'lifecare', 'radiology', 'homecarer', 'ehealth', 'paediatrics', 'life-support', 'medspa', 'styling', 'healthrelated', 'folk-medicine', 'aesthetics', 'childcare', 'homoeopath', 'healthworker', 'wellness', 'pharmacy', 'clinical', 'telemedical', 'biomedicine', 'medicare', 'pharma', 'preventative', 'nutrition', 'nurse-practitioner', 'medtech', 'cureall', 'care-taking', 'therapist', 'esthetics', 'telehealth', 'hospitaler', 'out-patient', 'baby-care', 'biopharmaceutical', 'paediatry', 'sanitarium', 'homoeopathism', 'health', 'sanitorium', 'panacaea', 'pediatry', 'anatomicomedical', 'aesculapian', 'pharmaceutic', 'medicine', 'gastroenterological', 'neurosurgical', 'psychopharmaceutical', 'medicamental', 'physiological', 'pharmacological', 'paraclinical', 'physicomedical', 'nonmedical', 'financial', 'photomedical', 'biochemical', 'clinic', 'diagnostic', 'radiological', 'medic', 'orthopaedic', 'biomedicinal',  'dental', 'ophthalmological', 'pediatric', 'medicotechnical', 'neurodiagnostic', 'cardiological', 'gynaecological', 'pharm', 'telemedicinal', 'medical', 'diagnostical', 'psychomedical', 'physicianary', 'iatric', 'hospital', 'geomedical', 'gynecological', 'nutritional', 'psychological', 'doctoral', 'premedical', 'paramedical', 'healthcare', 'veterinary', 'biomedical', 'cardiologic', 'medicational', 'biological', 'electromedical', 'obstetric', 'examination', 'oncological', 'checkup', 'pharmaceutical', 'medicinal', 'neurological', 'outpatient', 'obstetrical', 'orthopedic', 'sociomedical', 'cosmetic', 'medicamentary', 'surgical', 'psychiatric', 'dermatological', 'stomatological', 'emergency', 'otological', 'aeromedical']},
                    {"Insurance": ["insurance", 'insurer', 'mortgage', 'liability', 'bancassurance', 'cession', 'policyholder', 'uninsurable', 'assured', 'annuity', 'reinsure', 'safety', 'life', 'fidelity', 'insurable', 'takaful', 'hazard', 'retention', 'peril', 'risk', 'bordereau', 'allstate', 'moral', 'increasing', 'assurance', 'protection', 'claim', 'coverage', 'net', 'association', 'aval', 'guaranty', 'valued', 'microinsurance', 'security', 'reinsurance', 'insure', 'underwriting', 'valuation', 'uninsured', 'contingent', 'decreasing', 'noninsurance', 'cost','provision', 'guarantee', 'term', 'policy', 'underinsurance', 'viaticals', 'cover', 'bankassurance', 'indemnity', 'endowment', 'coinsurance', 'contract', 'compensation']},
                    {"SavingInvestingPayments": [ 'coin', 'purchases', 'fare', 'payback', 'outpayment', 'prepayment', 'paymeter', 'pay-off', 'tollage', 'rental', 'cash', 'money', 'deposit', 'underpayment', 'card', 'charge', 'billing','settling', 'disbursement', 'stipend', 'billpaying',  'dividend', 'settlement', 'paycheck', 'acquittance', 'invoice', 'paycheque', 'paytech', 'credit', 'disbursal', 'recompensation', 'paypal', 'loan', 'bills', 'remittance', 'expenditure', 'acquittal', 'cheque', 'consideration', 'paying', 'payout', 'payroll', 'fees', 'nonpayment', 'copay', 'changing', 'arrearage', 'wage', 'warrant', 'debts', 'payer', 'taxpayment', 'payee', 'receipt', 'biling', 'counter-payment', 'overpayment', 'defrayal', 'refund', 'rediscounting', 'remuneration', 'payoff', 'imbursement', 'defrayment', 'payable', 'advancement', 'inpayment', 'payment', 'debit', 'contribution', 'reimbursement', 'pay-out', 'repayment', 'pay', 'counterpayment', 'check', 'dues', 'counter', 'transaction', 'rebate','investee', 'business', 'spending', 'owning', 'divesting', 'purchasing', 'appreciating', 'buying', 'investible', 'entrepreneuring', 'banking', 'profiting', 'trading', 'selling', 'saving', 'investors', 'value', 'stakeholding', 'reselling', 'acquiring', 'revenue', 'overinvesting', 'funding', 'liquidating',  'allocating', 'procuring', 'capital', 'reinvestment', 'financing', 'wealthmaking', 'profit',  'economizing', 'investment', 'reallocating', 'stocks', 'coinvestment', 'stockbroking','money-making', 'renting', 'fund', 'underinvest', 'disinvesting', 'diversifying', 'earnings', 'evaluating']},
                    {"PersonalSpending": ["personal", 'hair', 'haircut', 'beard', 'gym', 'fitness', 'exercise','athletics', 'decor', 'decoration']},
                    {"RecreationEntertainment": ['drama', 'actor', 'sports', 'performing', 'stageplaying', 'socializing', 'movies', 'movie', 'showbiz', 'storytelling','music', 'play', 'play-acting', 'spectacle', 'entertainment', 'sport', 'nightlife', 'karaoke', 'gigging', 'beverage', 'marketing', 'arts', 'theatre', 'shopping', 'multimedia', 'social', 'comedy', 'box', 'display', 'culture', 'musical', 'light', 'variety', 'broadcasting', 'party', 'art', 'capade', 'extravaganza', 'costume', 'television', 'infotainment', 'interactive', 'entertaining', 'performance', 'media', 'recreation', 'show', 'intertainment', 'peoplewatching', 'catering', 'theater', 'animation', 'scene', 'theatrical',  'cinema', 'aquatic', 'gambling', 'escapism', 'leisuring', 'camping', 'creation', 'enhancement', 'recreationist', 'enjoyment', 'hiking', 'toying', 'dancing', 'leisure', 'pastime', 'wildlife', 'partaking', 'sportfishing', 'gaming', 'reagitation', 'parks', 'playground', 'recreative', 'cycling', 'disport',  'activites', 'activities', 'invigoration', 'outdoor', 'time', 'boating', 'fishing', 'distraction', 'recreationalists', 'tourism', 'diversion', 'hunting', 'relaxation', 'action', 'exploration', 'golfing', 'biking', 'eatertainment', 'retail', 'warfare']},
                    {"Miscellaneous": ["Miscellaneous"]},
                    ]

    usersDb.execute(
        "CREATE TABLE default_categories_table ( id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Education TEXT, Housing TEXT, Transportation TEXT, Food TEXT, Utilities TEXT, Insurance TEXT, MedicalHealthcare TEXT, SavingInvestingPayments TEXT, PersonalSpending TEXT, RecreationEntertainment TEXT, Miscellaneous TEXT);"
        )

    # Insert the dafault key words into the new table:
    keyWordsRows = []
    for i in range(126):
        newRow = []
        for category in categories:
            for cateName in category:
                try:
                    newRow.append(category[cateName][i])
                except IndexError:
                    newRow.append("NULL")
        keyWordsRows.append(newRow)
        # Adds each row of key words to the table, dividing them for their respective category
        usersDb.execute(
            "INSERT INTO default_categories_table (Education, Housing, Transportation, Food, Utilities, Insurance, MedicalHealthcare, SavingInvestingPayments, PersonalSpending, RecreationEntertainment, Miscellaneous) VALUES (?);",
            keyWordsRows[i])


''' Classify all the expenses in different budget categories and adds the categorized sheet to the database'''
# Main Budget Categories: https://www.quicken.com/blog/budget-categories/ ;
def classify(data, username, title):
    '''_____________Gets data_______________'''
    # Gets the user's budget categories;
    table = (username + "_categories")
    categories = usersDb.execute("SELECT * FROM ?;", table)
    userSheetList = (username + "_list")

    """_____ANALYZE AND CATEGORIZE EXPENSES BASED ON THE WORDS OF EACH EXPENSE:______"""
    categorized = categorize(data, categories, table)

    '''___________Adds the categorized items to the database in a new table__________;'''
    # Creates a new table to store this new expense classification "sheet"
    tableName = title
    database = ("sqlite:///" + "usersDatabases/" + username + ".db")
    database = SQL(database)
    database.execute(
        "CREATE TABLE ? (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, expense TEXT NOT NULL, value REAL NOT NULL, category TEXT NOT NULL)",
        tableName
    )

    # Inserts the name/id and the creation date/time of the new table in the user's list.
    dateTime = datetime.now()
    usersDb.execute(
        "INSERT INTO ? (dateTime, metric_tables_id) VALUES (?, ?)",
        userSheetList, dateTime, tableName
    )

    for category in categorized:
        categoryName = list(category.keys())[0]
        expense = category[categoryName][0]
        value = round((category[categoryName][1]), 2)
        database.execute(
            "INSERT INTO ? (expense, value, category) VALUES (?, ?, ?)",
            tableName, expense, value, categoryName
            )

#____________Used by classify to discover from what category each expense is____________
def categorize(data, categories, table):
    ''' Gets what's the last key word of the last category for posterior check if the word should be searched in dictionary for
    better categorization'''
    # Seize of table:
    size = len(categories)
    # Last Column:
    lastColumn = list(categories[0])[len(list(categories[0])) - 1]
    # Last Key:
    lastKey = usersDb.execute(
        "SELECT * FROM ? WHERE id = ?",
    table, size)
    lastKey = lastKey[0][lastColumn]

    # Holds categorized expenses;
    categorized = []
    # Holds already found expenses:
    found = []

    for expense in data:
        # Gets all the words in the expense name;
        words = getWords(expense[0])
        # Holds already searched words from the current expense;
        alreadySearched = []
        
        # Assure only expenses not categorized yet are searched
        if expense not in found:
            for word in words:
                # Holds how many rows the program iterated over
                count = 0
                for dictionary in categories:
                    count = count + 1
                    for category in dictionary:
                        # Checks if the current key word corresponds to the analyzed word
                        current = dictionary[category]
                        if word == current and expense not in found:
                            categorized.append({category:expense})
                            found.append(expense)
                            break

                        # Tries Categorize expenses by keywords in the meaningif ,f not able to categorize wihtout it;
                        elif current == lastKey and category == lastColumn and expense not in found and count == size and word not in alreadySearched:
                            alreadySearched.append(word)
                            # Used the following dictionary api https://dictionaryapi.dev/ ;
                            # Learned in https://pypi.org/project/python-freeDictionaryAPI/ ;
                            meaning = dictionaryApi(word)
                            # don't consider "none" (which means the word was not found in the api dictionary);
                            if meaning != "none":
                                for sentence in meaning:
                                    words.append(sentence)
                                    alreadySearched.append(sentence)
                            if meaning == "none" and word == words[len(words) - 1]:
                                found.append({"Miscellaneous":expense})
                                categorized.append({"Miscellaneous":expense})

                        # If not able to find the category for the expense, the category miscellaneous is atributed to it:
                        elif word == words[len(words) - 1] and current == lastKey and category == lastColumn and {"Miscellaneous":expense} not in categorized and expense not in found and count == size:
                            found.append({"Miscellaneous":expense})
                            categorized.append({"Miscellaneous":expense})
    return categorized


'''___________Functions used in categorize________________________'''
# Function used laterin classify function
# Receives a phrase and separates its words into a list of words;
def getWords(phrase):
    listOfWords = []
    newWord = ""

    # Iterates through the role phrase looking for spaces between words,
    # if one is found, the word is appended to the list of words and other one is searched
    for i in range(len(phrase)):
        if phrase[i].isalpha():
            newWord = newWord + phrase[i]
        if phrase[i] in [" ", "\n", "\0"] and phrase[i-1].isalpha() or i == (len(phrase) - 1):
            # Don't consider prepositions words;
            # List of prepositions or conjunctions found in https://www.englishclub.com/grammar/prepositions-list.php
            # and https://7esl.com/conjunctions-list/ ;
            newWord = newWord.lower()
            if newWord not in ['aboard', 'about', 'above', 'across', 'after', 'against', 'along', 'amid', 'among', 'anti', 'around', 'as', 'at', 'before', 'behind', 'below', 'beneath', 'beside', 'besides', 'between', 'beyond', 'but', 'by', 'concerning', 'considering', 'despite', 'down', 'during', 'except', 'excepting', 'excluding', 'following', 'for', 'from', 'in', 'inside', 'into', 'like', 'minus', 'near', 'of', 'off', 'on', 'onto', 'opposite', 'outside', 'over', 'past', 'per', 'plus', 'regarding', 'round', 'save', 'since', 'than', 'through', 'to', 'toward', 'towards', 'under', 'underneath', 'unlike', 'until', 'up', 'upon', 'versus', 'via', 'with', 'within', 'without',"an", 'no', 'whoever', 'either', 'while', 'if', 'after', 'nor', 'whether', 'whereas', 'whenever', 'neither', 'also', 'so', 'unless', 'supposing', 'and', 'why', 'not', 'because', 'both', 'only', 'when', 'what', 'whose', 'although', 'since', 'how', 'rather', 'till', 'until', 'before', 'than', 'or', 'sooner', 'such', 'wherever', 'the', 'as', 'just', 'but', 'that', 'then', 'where']:
                listOfWords.append(newWord)
            newWord = ""

    return listOfWords

# Used the following dictionary api https://dictionaryapi.dev/ ;
# Learned in https://pypi.org/project/python-freeDictionaryAPI/ ;
# Returns the meaning of the word received
def dictionaryApi(term):
    with DictionaryApiClient() as client:
        try:
            parser = client.fetch_parser(term)
        except:
            return "none"
        word = parser.word
        meaning = word.meanings[0]
        meaning = str(meaning.definitions)
        definition = ""

        # Edits the meaning for the purpose of being succinct;
        add = False
        for i in range(len(meaning)):
            if meaning[i] == "'" and meaning[i - 1] == "=":
                add = True

            if add == True and meaning[i].isalpha() or add == True and meaning[i] == " ":
                definition = definition + meaning[i]

            if meaning[i] == "'" and meaning[i + 1] == ",":
                add = False

        definition = getWords(definition)
        if term in definition:
            definition.remove(term)

        return definition

# Gets the total amount spent in each category putting it in a dictionary and a list with all the categories
# in the analyzed table;
def totalExpensePerCategorie(username, tableName):
    # Gets user database
    database = ("sqlite:///" + "usersDatabases/" + username + ".db")
    database = SQL(database)

    # Gets all the data from the desired table
    table = database.execute(
        "SELECT * FROM ?;", tableName
        )
    
    
    # Sum all the price/values of each category and add the pair category and total value to a dict;
    categoriesAmount = {}
    categories = []
    
    for item in table:
        category = item["category"]
        if category not in categories:
            categoriesAmount[category] = item["value"]
            categories.append(category)
        else:
            categoriesAmount[category] = categoriesAmount[category] + item["value"]

    list = []
    list.append(categoriesAmount)
    list.append(categories)
    
    return list


# Aesthetics of Graph: treat categories words for printing in graph with spaces
def treatCategories(categories):
    word = ""
    newCategories = []
    for item in categories:
        length = len(item)
        for i in range(1, length):
            if i == 1:
                word = word + item[0]
            if item[i-1].islower() and item[i].isupper():
                word = word + " " + item[i]
            else:
                word = word + item[i]
            if i == (length - 1):
                newCategories.append(word)
                word = ""
    return newCategories


# Get's all the user's personal categories;
def personalCategories(username):
    tableName = username + "_categories"
    # Gets all the data from the desired table
    table = usersDb.execute(
        "SELECT * FROM ? LIMIT 1 ;", tableName
        )

    # Gets all the categories the user have in it's personal categories table:
    categories = []
    tableList = list(table[0].keys())
    for i in range(1, len(tableList)):
        categories.append(tableList[i])

    return categories


def deleteUser():
    user_id = session["user_id"]
    username = usersDb.execute("SELECT username FROM users WHERE id = ?;", user_id)
    username = username[0]['username']
    usersDb.execute("DROP TABLE ?;", (username + "_categories"))
    usersDb.execute("DROP TABLE ?;", (username + "_list"))
    usersDb.execute("DELETE FROM users WHERE username = ?;", username)
    database = ("usersDatabases/" + username + ".db")
    os.remove(database)


