# Import all the necessary libraries to make the website work
import os
# Used pip install to install pandas library, used to manipulate excel files;
import pandas as pd;
# Used matplotlib to build the basic expense graphs for the user's dashboard.
from matplotlib import pyplot as plt
from PIL import Image
from cs50 import SQL # Used to pass commands to SQL
from flask import Flask, flash, redirect, render_template, jsonify, url_for, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import *
# Used to check user's filename, like that old saying “never trust user input”.
# Learned in: https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/;
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
import json


# Path of where uploaded files will be stored:
UPLOAD_FOLDER = "uploads"

# Configure web application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
Session(app) 

# Configure CS50 Library to use SQLite database inside python
usersDb = SQL("sqlite:///users.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        return
    else:
        return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # If there was any user before, it is erased from session, for other one to enter;
    session.clear()

    if request.method == "POST":
        # Gets user input for login:
        username = request.form.get("username")
        password = request.form.get("password")

        # Gets all usernames an passwords in users dabase to see if it's a valid one:
        rows = usersDb.execute("SELECT * FROM users WHERE username = ?;", username)
        if len(rows) != 1 or not username or not password or not check_password_hash(rows[0]["hash"], password):
            return render_template("login.html", apology="Incorrect username or password")

        # If passed through all checks a session with the user id is created and he/she is redirected to the homepage;
        session["user_id"] = rows[0]["id"]
        return redirect('/')

    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():
    if request.method == "GET":
        # If logout is pressed session is cleared and the user is redirected to the login page;
        session.clear()
        return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Gets all the register information passed by the user;
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        password1 = request.form.get("password1")

        ''' Checks if the register information passed by the user is valid: '''
        if not name:
            return render_template("register.html", apology="400: Please, enter a valid name.")
        # Gets all usernames in users dabase to see if it's not one that is already in use:
        usernames = usersDb.execute("SELECT COUNT(username) FROM users WHERE username = ?;", username)
        if usernames[0]["COUNT(username)"] != 0:
            return render_template("register.html", apology="Username already in use.")
        if " " in username:
            return render_template("register.html", apology="Username can't contain spaces.")
        if not password or not password1:
            return render_template("register.html", apology="Please, enter a password.")
        if len(password) < 5:
            return render_template("register.html", apology="Please, enter a password with at least 5 characters.")
        if password != password1:
            return render_template("register.html", apology="Passwords are different.")

        # Hash password for safety:
        password = generate_password_hash(password)

        ''' If all checks are passed and valid, a place in the users table and a list of all the tables that the user might use are created;'''
        # Creation of personal table list_of_tables, wich will hold the names of all tables that store different period Expenses Panel;
        usersDb.execute(
            "CREATE TABLE ? (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, dateTime TEXT NOT NULL, metric_tables_id TEXT NOT NULL);",
            (username + "_list"))

        # Creates a table that holds all the main budget categories with of the user their respective keywords;
        create_categories_table(username)

        # Creates a database for all of the classified sheets of the user:
        databaseName = ("usersDatabases/" + username + ".db")
        open(databaseName, "x")

        # Adds user to the database:
        usersDb.execute(
            "INSERT INTO users (name, username, hash, list_of_tables, personal_categories_table) VALUES (?, ?, ?, ?, ?);",
        name, username, password, (username + "_list"), (username + "_categories")
            )
        return redirect("/login")

    else:
        return render_template("register.html")


# Uploads, process and classify sheets uploaded by the user
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        '''________ Gets and checks validity_________'''
        # Gets the name for the desired Expenses Panel:
        name = request.form.get("name")
        # Checks if name is valid:
        if len(name) < 2:
            return render_template("upload.html", placeholder=2)

        # Will hold the information of excel file uploaded
        data = []
        file = request.files['file']

        if not file.filename:
            return render_template("upload.html", placeholder=1)
        
        # Check if it is a secure filename;
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Check if the file is an excel (xlsx) type or not:
        # Learned to get file extensions in: https://www.digitalocean.com/community/tutorials/get-file-extension-in-python;
        fileType = os.path.splitext(filename)
        if not filename or fileType[len(fileType) - 1] != ".xlsx":
            return render_template("upload.html", placeholder=1)

        # Save file in its proper place;
        file.save(path)
    
        # Gets the data of the file and pass it to the data list:
        dataframe = pd.read_excel(("uploads/" + filename))
        dataframe = dataframe[dataframe.columns.drop(list(dataframe.filter(regex='Unnamed:')))].to_dict('split')
        data.append(dataframe["columns"])

        # Checks if it's a valid sheet for analysis
        if len(dataframe["columns"]) != 2:
            return render_template("upload.html", placeholder=1)
            # Deletes file after being used:
            os.remove(path)

        # Deletes file after being used:
        os.remove(path)

        for expense in dataframe["data"]:
            data.append(expense)

        # Gets user's sheets list name
        username = getUsername()

        # Treats the aesthetic format of title to fit correctly in SQL database:
        title = makeTitle(name)

        userSheetList = (username + "_list")

        # Checks if there's no table with the same name that the user wants:
        listOfNames = usersDb.execute("SELECT metric_tables_id FROM ?;", userSheetList)
        for item in listOfNames:
            if item["metric_tables_id"] == title:
                return render_template("upload.html", placeholder=2)
            
        '''__________Process data_________'''
        # Uses helper function to classify each expense from the data;
        classify(data, username, title)
        return redirect("/dashboard")
    else:
        return render_template("upload.html")


@app.route("/dashboard", methods=["GET", "POST"])   
@login_required
def dashboard():
    # Gets username
    username = getUsername()
        
    if request.method == "POST":

        '''________Deletion of desired sheets (ONCLICK)_________'''
        # Deletion: Checks if the user wants to delete any sheet from database, if so, it is deletede;
        deleteItem = request.form.get("delete")
        if deleteItem:
            deleteSheet(deleteItem, username)
            
        
        # If no sheet was deleted:
        #______________Gets and treat data from the user's selected table______________________
        # Gets the name of the table the user wants to get the basic dashboard from;
        tableName = request.form.get("sheet")
        # Checks if table variable is a valid one:
        if not tableName:
            return redirect("/dashboard")

        # List that contains a dictionary with the total amount spent in each category
        # and other list with all the categories in the analyzed table
        lists = totalExpensePerCategorie(username, tableName)
        categoriesAmount = lists[0]
        categories = lists[1]

        # Creates a list with the total costs of each category:
        costs = []
        for category in categoriesAmount:
            costs.append(categoriesAmount[category])
        

        '''____________________Graph Creation_________________________'''
        # Creates a graph based on the pair category / total costs:

        # Aesthetics of Graph: treat categories words for printing in graph with spaces
        categoriesEdit = treatCategories(categories)
        
        # Better visualization: adjust the size of the image based on how many categories it has;
        for category in categories:
            if len(category) >= 10:
                plt.figure(figsize = (35, 5)) 
                break
            else:
                plt.figure(figsize = (20, 5))

        # Sets the labels:
        plt.rcParams.update({'font.size': 14})
        plt.ylabel("Cost ($)", fontweight='bold', fontsize="17")
        plt.xlabel("Categories", fontweight='bold', fontsize="17")
        plt.bar(categoriesEdit, costs)
        plt.grid()
        plt.show()
        imageFile = ("static/plotImages/" + username + ".png")
        plt.savefig(imageFile)


        '''______________________Edit Table (OUTPUT)_______________________'''
        # Creation of table where the user can manually edit the category of his/her expenses:

        # All the user's personalCategories
        personal = personalCategories(username)
        personal = treatCategories(personal)

        # Converts the current table to a list
        tableRows = []
        database = ("sqlite:///" + "usersDatabases/" + username + ".db")
        database = SQL(database)
        # Gets all the data from the desired table
        table = database.execute(
        "SELECT * FROM ?;", tableName
        )

        # Aesthetics: Put spaces between words, and converts the cost of each expense to dollar;
        for row in table:
            row['category'] = (treatCategories([row['category']]))[0]
            row['value'] = '${:,.2f}'.format(row['value'])

        return render_template("dashboard.html", tableName=tableName, source=imageFile, table=table, personalCategories=personal)
         

    else:
        # Gets the list of all categorized sheets the user have;
        sheetsList = usersDb.execute(
            "SELECT metric_tables_id FROM ? ORDER BY id DESC;",
            (username + "_list")
        )

        placeholder = []

        for item in sheetsList:
            placeholder.append((item["metric_tables_id"]))
         # Passes placeholer with all the categorized sheets the user have;
        return render_template("dashboardList.html", placeholder=placeholder)


@app.route("/dashboard/edit", methods=["POST"])   
@login_required   
def dashboardEdit():
    # Gets username
    username = getUsername()
        
    if request.method == "POST":
        '''____________User's Expenses Categories edit/change (ACTIVATED IN SELECT OPTIONS)______________'''
        changes = request.get_json()
        if changes:
            tableName = changes['Changes'][0]
            changeRequests = changes['Changes'][1]
            userDatabase = ("sqlite:///" + "usersDatabases/" + username + ".db")
            userDatabase = SQL(userDatabase)

            # Edits the categories in the desired table as requested by the user:
            for change in changeRequests:
                # Checks if it's a valid change of categories:
                currentCategory = userDatabase.execute(
                "SELECT category FROM ? WHERE id = ?;",
                tableName, change['expenseId']
                )
                currentCategory = currentCategory[0]['category']
                if currentCategory != change['newCategory']:
                    # Changes categories:
                    userDatabase.execute(
                        "UPDATE ? SET category = ? WHERE id = ?;",
                        tableName, change['newCategory'], change['expenseId']
                        )
                    '''_________________Categories adapt to word (new Keyword):__________'''
                    expense = userDatabase.execute(
                        "SELECT expense FROM ? WHERE id = ?;",
                        tableName, change['expenseId']
                        )
                    expense = expense[0]['expense']
                    adaptKeywords(expense, change['newCategory'], username)

            return redirect("/dashboard")
    else:
        return render_template("apology.html", placeholder="Not a valid Method")


@app.route("/categories", methods=["GET", "POST"])   
@login_required 
def categories():
    username = getUsername()

    if request.method == "POST":
        # Gets posted information:
        createCategory = request.form.get("create")
        delete = request.form.get("delete")
        categoryEdit = request.form.get("category")

        if createCategory:
            return redirect("/categoryCreation")
        
        if delete:
            userCategories = (username + "_categories")
            usersDb.execute("ALTER TABLE ? DROP COLUMN ?;", userCategories, delete)
            return redirect("/categories")
        
        if categoryEdit:
            return redirect(url_for("categoryEdition", categoryEdit=categoryEdit))
        
        return redirect("/categories")
    
    else:
        personal= personalCategories(username)
        personalEdited = treatCategories(personal)
        return render_template("categories.html", personal_categories=personal, personalEdited=personalEdited)
    

@app.route("/categoryCreation", methods=["GET", "POST"])   
@login_required 
def createCategory():
    if request.method == "POST":
        '''________ Gets and checks variables validity_________'''
        newCategoryName = request.form.get("newCategoryName")
        keywords = request.form.get("keywords")

        # Treats the aesthetic format of category title to fit correctly in SQL database:
        categoryTitle = makeTitle(newCategoryName)
        username = getUsername()

        personal = personalCategories(username)

        if len(categoryTitle) < 2 or categoryTitle in personal or categoryTitle in ["id", "ID", "Id", "iD"]:
            return render_template("categoryCreation.html", placeholder="A bigger name is necessary or category already exists.")
        
        keywordsList = getWords(keywords)
        if len(keywordsList) < 1:
            return render_template("categoryCreation.html", placeholder="Please, enter at least one keyword.")
        
        categoryCreator(categoryTitle, keywords, username)

        return render_template("categoryCreation.html", placeholder=0)

    else:
        return render_template("categoryCreation.html")



@app.route("/categoryEdition", methods=["GET", "POST"])   
@login_required 
def categoryEdition():
    username = getUsername()

    if request.method == "POST":
        categoryEdit = request.get_json()
        userCategories = username + "_categories" 

        # Deletes keywords if the user selected any to delete;
        if len(categoryEdit) == 2:
            deleteKeyword = categoryEdit[0]['deleteKeyword']
            oldCategory = categoryEdit[1]['oldCategory']
            sqlText = "UPDATE " + userCategories + " SET " + oldCategory + " = \"NULL\" WHERE "  + oldCategory + " = \"" + deleteKeyword + "\";"
            usersDb.execute(sqlText)
            return redirect(url_for("categories"))

        else:
            categoryOldName = categoryEdit[0]['categoryEdit']
            newCategoryName = categoryEdit[1]['newCategoryName']
            category = categoryOldName
        
        newKeywords = categoryEdit[2]['newKeywords']

        if len(newCategoryName) > 2 and newCategoryName not in ['NULL','Null','\0', 'None', None]:
            newCategoryName = makeTitle(newCategoryName)
            if ' ' not in newCategoryName:
                sqlText = ("ALTER TABLE " + userCategories + " RENAME COLUMN " + categoryOldName + " TO " + newCategoryName + ";")
                usersDb.execute(sqlText)
                category = newCategoryName

        if newKeywords and len(newKeywords) > 2 and newKeywords not in ['NULL','Null','\0', 'None', None]:
            adaptKeywords(newKeywords, category, username)

        return redirect(url_for("categories"))
    
    else:
        categoryEdit = request.args.get("categoryEdit")
        if categoryEdit:
            categoryTreated = treatCategories([categoryEdit])[0]
            keywords = getKeywords(categoryEdit, username)
        else:
            return redirect("/categories")

        return render_template("categoryEdit.html", categoryEdit=categoryEdit,categoryName=categoryTreated, keywords=keywords)
        

@app.route("/delete-user", methods=["GET", "POST"])   
@login_required
def deletUser():
    if request.method == "POST":
        deleteUser()
    
    return redirect("/login")

app.run(debug = True)