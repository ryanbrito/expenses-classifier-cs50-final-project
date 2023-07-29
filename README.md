![Application Banner](banner.png)

<div align="left" style="margin-top: -1%">
    <a href="https://www.python.org/">
        <image src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue">
    </a>
    <a href="https://flask.palletsprojects.com/en/2.3.x/">
        <image src="https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white">
    </a>
    <a href="https://www.sqlite.org/index.html">
        <image src="https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white">
    </a>
    <a href="https://www.w3.org/html/">
        <image src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white">
    </a>
    <a href="https://www.w3.org/Style/CSS/Overview.en.html">
        <image src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white">
    </a>
    <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript">
        <image src="https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E">
    </a>
    <a href="https://getbootstrap.com/">
        <image src="https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white">
    </a>
    <a href="https://www.json.org/json-en.html">
        <image src="https://img.shields.io/badge/json-5E5C5C?style=for-the-badge&logo=json&logoColor=white">
    </a>
    <a href="https://matplotlib.org/">
        <image src="https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black">
    </a>
    <a href="https://pandas.pydata.org/">
        <image src="https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white">
    </a>
</div>

# Expenses Panel - CS50 Final Project
## Video Demo: [ Expenses Panel - CS50x 2023 - Final Project. ](https://www.youtube.com/watch?v=-oqbUjXRCGQ)
## Description:
Expenses Panel is a basic web application developed to get your expense sheets (maybe your bank extract or your personal monthly expenses sheet), automatically classify these expenses into main budget categories (or your own created ones), and build a dashboard. As a result, it helps the user understand, organize, and plan their expenses more effectively.

### Features:
* Automatically classify expenses into budget categories;
* Automatically create expenses dashboard;
* Creation and edition of categories;

## How to Install and Run the Project:
* Install and Use WSL Ubuntu for convenience;
* Install all packages running the following in terminal:
```
git clone https://github.com/RyanBrito/expenses-panel-cs50-final-project.git
pip install -r requirements.txt
python app.py
```
* Use the link prompted in terminal to access the application via flask development server;

## How to Use the Project:
* Check the folder "Expenses sheet examples" for rapid examples of expenses sheets that you can upload to the application;
* More usage information in the video[ Expenses Panel - CS50x 2023 - Final Project. ](https://www.youtube.com/watch?v=-oqbUjXRCGQ);

## How it works:
### These diagram videos shows how the application's primary function - categorize() - works and automatically classifies each expense.
* Imagine an expense in your sheet that looks like "Gasoline | $200.00".<br>
"DIAGRAM 1"

* The application will use dictionary API  if it can't find any word of the expense title in the categories table. Take the following example where the application iterated through the whole table and could not categorize the expense "Peanut Butter | $10.00".<br>
"DIAGRAM 2"

## Files and Folders:
### app.py:
 app.py is the main file in the project; it contains all the routes the user can access in the web application, check if the user entered valid responses, and directs helper functions to their correct and respective places.

### helpers.py:
 It contains all the helper functions used in app.py, helping it become cleaner and more succinct. It also holds the primary function of the application, named categorize, which is the one that gets the expense title and, based on their words, tries to classify to which category it belongs.

### templates folder:
 Carries all the html files, each corresponding to a different page, except for layout.html, which is the default layout used in all pages with Jinja's help. It is important to remember that the templates folder is required, belonging to the [standard layout of Flask applications](https://flask.palletsprojects.com/en/2.3.x/tutorial/layout/).

### static folder:
The static folder - which also belongs to the standard layout of Flask applications - contains assets used by the templates, including CSS files, JavaScript files, and images.
* JavaScript: is used in this application to post information - in JSON format - to the server's application, redirect some pages, and alert/inform users of loading processes and requirements.
* styles.css: holds the styling of pages and assets, complementing Bootstrap.

### usersDatabases folder:
Have a database for each user, where each table store an uploaded, formatted file ( already got the name, expenses titles, and costs);

### users.db:
 This database has four main tables: default_categories_table, users, "username"_categories (one per user), and "username"_list (one per user). OBS: In place of "username" goes the user's actual username.
 * default_categories_table: contains the default budget categories (based on the information found in [FIRST BANK](https://localfirstbank.com/article/budgeting-101-personal-budget-categories/) and [Quicken](https://www.quicken.com/blog/budget-categories/)) and the respective keywords related to each one;
 * users.db: holds, for each user, the id, name, username, hashed password, user's list table name, and user's category table name;
 * "username"_categories: This table type holds the user's categories with their respective keywords. The user has specific control over this table; he/she can delete, add, or edit categories (even default ones) and keywords;
 * "username"_list: have the name of all expense tables stored in the user's database in usersDatabases folder;

### requirements.txt:
Possess the name of all required packages necessary to run the application.

## Problems and future of the application:
### Problems:
* The application is strict in the type and format of the document to upload; it only accepts Excel documents with only two columns, expenses names, and costs;
* Categorization mechanism can be more efficient;
### Future:
* Raise efficiency of Categorization using binary search;
* Accept a wider variety of types of documents, like different formats of pictures, csv, and pdf;
* Accept substantial documents, like different year's expense files;
* Improve application using machine learning to automatically identify the expenses, actual cost, and the respective period - more of a Bottom-Up approach.