# Import all the necessary libraries to make the website work
import os
# Used pip install to install pandas library, used to manipulate excel files;
import pandas as pd;
# Used matplotlib to build the basic expense graphs for the user's dashboard.
from matplotlib import pyplot as plt
from PIL import Image
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, create_categories_table, classify, deleteUser, treatCategories
# Used to check user's filename, like that old saying “never trust user input”.
# Learned in: https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/;
from werkzeug.utils import secure_filename
from freedictionaryapi.clients.sync_client import DictionaryApiClient
from datetime import datetime

# Configure CS50 Library to use SQLite database inside python
usersDb = SQL("sqlite:///users.db")

def caller():
    data = []
    dataframe = pd.read_excel(("uploads/" + "Budget.xlsx"))
    dataframe = dataframe[dataframe.columns.drop(list(dataframe.filter(regex='Unnamed:')))].to_dict('split')
    data.append(dataframe["columns"])
    for expense in dataframe["data"]:
                data.append(expense)
    title = "thetest"
    username = "ryan"

    classify(data, username, title)

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

    # Holds categorized expenses with their categories;
    categorized = []
    # Holds already found expenses:
    found = []

    for expense in data:
        # Gets all the words in the expense name;
        words = getWords(expense[0])
        # Holds already searched words from the current expense;
        alreadySearched = []

        count = 0

        for dictionary in categories:
            count = count + 1
            for category in dictionary:
                # Assure only expenses not categorized yet are searched
                if expense not in found:
                    # Checks if any of the words of the expense is a key word of any category, if so, it's own category is found;
                    for word in words:
                        if "oats" in words:
                            print(words)
                        if word == "food" and "oats" in words:
                            print(word +"  "+ current + ' found____________________________________________________________________')
                        if word == "food" and current == "food":
                            print(word +"  "+ current + ' correct____________________________________________________________________')
                    
                        current = dictionary[category]
                        if current != 'NULL' and word == current:
                            if {"miscellaneous":expense} in categorized:
                                categorized.remove({"miscellaneous":expense})
                            categorized.append({category:expense})

                            for curr in words: ####
                                alreadySearched.append(curr)###
                            found.append(expense)

                            if word == "oats":
                                print(word + 'KKKKKKKKKKKKK____________________________________________________________________')

                            break

                        # Tries Categorize expenses by keywords in the meaning, if not able tocategorize wihtout it;
                        elif dictionary[category] == lastKey and category == lastColumn and {"miscellaneous":expense} not in categorized and expense not in found and count == size:
                            if word not in alreadySearched and word in words:
                                # Used the following dictionary api https://dictionaryapi.dev/ ;
                                # Learned in https://pypi.org/project/python-freeDictionaryAPI/ ;
                                meaning = dictionaryApi(word)
                                # don't consider "none" (which means the word was not found in the api dictionary);
                                if meaning != "none":
                                    for sentence in meaning:
                                        if word == "oats":
                                            print(word + " and " + sentence +' - sentence____________________________________________________________________')
                                        alreadySearched.append(sentence)
                                        words.append(sentence)

                                # If not able to find the category for the expense, the category miscellaneous is atributed to it:
                                else:
                                    categorized.append({"miscellaneous":expense})
                            else:
                                categorized.append({"miscellaneous":expense})
    print(categorized)
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
     


caller()