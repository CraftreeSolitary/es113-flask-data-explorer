from flask import Flask, render_template, request, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField
from wtforms import widgets
from wtforms.validators import DataRequired
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)

# Secret Key!
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"

# Configure db
db = yaml.safe_load(open('db.yaml'))

app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config ['MYSQL_PASSWORD'] = db['mysql_password']
app.config ['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

# This code from WTForms docs, this class changes the way SelectMultipleField
# is rendered by jinja
# https://wtforms.readthedocs.io/en/3.0.x/specific_problems/
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ColumnForm(FlaskForm):
    bond_number = StringField("Enter Bond Number")
    select_multiple_field = MultiCheckboxField(choices = ["Reference No (URN)", "Journal Date", "Date of Purchase", "Date of Expiry", "Name of the Purchaser", "Purchase Prefix", "Redemption Prefix", "Purchase Denominations", "Redemption Denominations", "Issue Branch Code", "Issue Teller", "Date of Encashment", "Name of the Political Party", "Account no. of Political Party", "Pay Branch Code", "Pay Teller"])
    submit = SubmitField()

class CompanyForm(FlaskForm):
    company = StringField("Enter Company/Individual Name")
    submit = SubmitField()

class PartyForm(FlaskForm):
    party = StringField("Enter Name of Political Party")
    submit = SubmitField()

@app.route("/")
def index():
    cur = mysql.connection.cursor()
    cur.execute("select `Name of the Purchaser`, `Name of the Political Party`, `Redemption Denominations` from purchase_details as pd right join redemption_details as rd on rd.`Bond Number`=pd.`Bond Number`;")
    data = cur.fetchall()
    table = []
    for row in data:
        table.append([row[0], row[1], int("".join(row[2].split(",")))])
    cur.close()
    return render_template("index.html", table=table)

@app.route("/search", methods = ["GET", "POST"])
def search():
    form = ColumnForm()
    bond_number = None
    table = None
    headings = None
    if request.method == "POST":
        bond_number = form.bond_number.data
        headings = tuple(form.select_multiple_field.data)
        form.bond_number.data = None
        form.select_multiple_field.data = None
    if bond_number:
        cur = mysql.connection.cursor()
        cur.execute("select " + ",".join(["`"+x+"`" for x in headings]) + f" from purchase_details as pd right join redemption_details as rd on rd.`Bond Number`=pd.`Bond Number` where pd.`Bond Number` = {bond_number};")
        table = cur.fetchall()
        cur.close()
    return render_template("search.html", form=form, bond_number=bond_number, table=table, headings=headings)

@app.route("/company_individual_stats", methods = ["GET", "POST"])
def company_individual_stats():
    form = CompanyForm()
    company = None
    table = None
    xaxis = None
    yaxis = None
    yaxis2 = None
    if request.method == "POST":
        company = form.company.data
        form.company.data = None
    if company:
        cur = mysql.connection.cursor()
        cur.execute(f"select `Date of Purchase`, `Purchase Denominations` from purchase_details as pd right join redemption_details as rd on rd.`Bond Number`=pd.`Bond Number` where `Name of the Purchaser` = '{company.upper()}';")
        data = cur.fetchall()
        cur.close()
        table = []
        data_dict = {}
        # year : (value, count)
        for row in data:
            if int(str(row[0])[:4]) in data_dict:
                data_dict[int(str(row[0])[:4])][0] += int("".join(row[1].split(",")))
                data_dict[int(str(row[0])[:4])][1] += 1
            else:
                data_dict[int(str(row[0])[:4])] = [int("".join(row[1].split(","))), 1]
        for year in data_dict:
            table.append((year, data_dict[year][0], data_dict[year][1]))
        table = tuple(table)
        xaxis = [row[0] for row in table]
        yaxis = [row[1] for row in table]
        yaxis2 = [row[2] for row in table]
    return render_template("company_individual_stats.html", form=form, company=company, table=table, xaxis = xaxis, yaxis = yaxis, yaxis2=yaxis2)

@app.route("/political_party_stats", methods = ["GET", "POST"])
def political_party_stats():
    form = PartyForm()
    party = None
    table = None
    xaxis = None
    yaxis = None
    yaxis2 = None
    if request.method == "POST":
        party = form.party.data
        form.party.data = None
    if party:
        cur = mysql.connection.cursor()
        cur.execute(f"select `Date of Encashment`, `Redemption Denominations` from purchase_details as pd right join redemption_details as rd on rd.`Bond Number`=pd.`Bond Number` where `Name of the Political Party` = '{party.upper()}';")
        data = cur.fetchall()
        cur.close()
        table = []
        data_dict = {}
        # year : (value, count)
        for row in data:
            if int(str(row[0])[:4]) in data_dict:
                data_dict[int(str(row[0])[:4])][0] += int("".join(row[1].split(",")))
                data_dict[int(str(row[0])[:4])][1] += 1
            else:
                data_dict[int(str(row[0])[:4])] = [int("".join(row[1].split(","))), 1]
        for year in data_dict:
            table.append((year, data_dict[year][0], data_dict[year][1]))
        table = tuple(table)
        xaxis = [row[0] for row in table]
        yaxis = [row[1] for row in table]
        yaxis2 = [row[2] for row in table]
    return render_template("political_party_stats.html", form=form, party=party, table=table, xaxis = xaxis, yaxis = yaxis, yaxis2=yaxis2)

@app.route("/party_donation_stats", methods = ["GET", "POST"])
def party_donation_stats():
    form = PartyForm()
    party = None
    table = None
    total = None
    xaxis = None
    yaxis = None
    if request.method == "POST":
        party = form.party.data
        form.party.data = None
    if party:
        cur = mysql.connection.cursor()
        cur.execute(f"select `Name of the Purchaser`, `Purchase Denominations` from purchase_details as pd right join redemption_details as rd on rd.`Bond Number`=pd.`Bond Number` where `Name of the Political Party` = '{party.upper()}';")
        data = cur.fetchall()
        table = []
        cur.close()
        total = 0
        xaxis = []
        yaxis = []
        donation = {}
        for row in data:
            if row[0] and row[1] is not None: # removing missing data
                table.append((row[0], int("".join(row[1].split(",")))))
                total += int("".join(row[1].split(",")))
                if row[0] in donation:
                    donation[row[0]]+=int("".join(row[1].split(",")))
                else:
                    donation[row[0]]=int("".join(row[1].split(",")))
        for company in donation:
            xaxis.append(company)
            yaxis.append(donation[company])
        table = tuple(table)
    return render_template("party_donation_stats.html", form=form, party=party, table=table, total = total, xaxis=xaxis, yaxis=yaxis)

@app.route("/company_donation_stats", methods = ["GET", "POST"])
def company_donation_stats():
    form = CompanyForm()
    company = None
    table = None
    total = None
    xaxis = None
    yaxis = None
    if request.method == "POST":
        company = form.company.data
        form.company.data = None
    if company:
        cur = mysql.connection.cursor()
        cur.execute(f"select `Name of the Political Party`, `Redemption Denominations` from purchase_details as pd right join redemption_details as rd on rd.`Bond Number`=pd.`Bond Number` where `Name of the Purchaser` = '{company.upper()}';")
        data = cur.fetchall()
        table = []
        cur.close()
        total = 0
        xaxis = []
        yaxis = []
        donations = {}
        for row in data:
            if row[0] and row[1] is not None: # removing missing data
                table.append((row[0], int("".join(row[1].split(",")))))
                total += int("".join(row[1].split(",")))
                if row[0] in donations:
                    donations[row[0]]+=int("".join(row[1].split(",")))
                else:
                    donations[row[0]]=int("".join(row[1].split(",")))
        for party in donations:
            xaxis.append(party)
            yaxis.append(donations[party])
        table = tuple(table)
    return render_template("company_donation_stats.html", form=form, company=company, table=table, total = total, xaxis=xaxis, yaxis=yaxis)
