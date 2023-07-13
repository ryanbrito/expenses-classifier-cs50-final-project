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



# Gets username
username = "ryan" ######
tableName = username + "_categories"
# Gets user's category table
usersDb = SQL("sqlite:///users.db") ####
# Gets all the data from the desired table
table = usersDb.execute(
    "SELECT * FROM ? LIMIT 1 ;", tableName
    )

# Gets all the categories the user have in it's personal categories table:
categories = []
tableList = list(table[0].keys())
for i in range(1, len(tableList)):
    categories.append(tableList[i])

print(categories)