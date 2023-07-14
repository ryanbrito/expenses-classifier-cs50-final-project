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
import string

# Configure CS50 Library to use SQLite database inside python
usersDb = SQL("sqlite:///users.db")

def remove(word):
    return word.translate('',' \n\t\r')

def printer():
    
    title = "the test \n23"
    title = title.title()
    scape = ' \n\t\r'
    title = title.translate(str.maketrans('','',scape))
    print(title)

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


printer()