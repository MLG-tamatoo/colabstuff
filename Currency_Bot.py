import discord
import time
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

"""configuration"""

bot = commands.Bot(command_prefix = "!")
client = discord.Client()

app = Flask(__name__)

app.config['SECRET_KEY'] = "tamatoo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

'''making the sqlDB models'''

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    money = db.Column(db.String(100), default="100", nullable=False)
    total_stock_value = db.Column(db.String(100), default="0", nullable=False)
    stocks = db.relationship('Stock', backref='owner', lazy=True)
    def __repr__(self):
        return f"User('{self.username}, {self.money}, {self.total_stock_value}, {self.stocks}, {self.id}')"


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(10000), nullable=False)
    state = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    def __repr__(self):
        return f"Stock('{self.company_id}, {self.value}, {self.id}, {self.state}')"

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    company_value = db.Column(db.String(10000), default="0", nullable=False)
    stocks = db.relationship('Stock', backref='author', lazy=True)
    old_stock_number = db.Column(db.String(100), default="0", nullable=False)
    def __repr__(self):
        return f"Company('{self.company_name}, {self.company_value}, {self.stocks}, {self.id}')"

"""commands"""
@client.event
async def on_ready():
    print("bot is ready")

@client.event
async def on_message(context):

    # makeing global functions and lists and variables
    stop = False
    admins = ["tamatoo"]
    def update_user(user):
        print("updating user")
        for i in user.stocks:
            stock = i
            company = Company.query.filter_by(company_id=stock.company_id).first()
            stock.value = (company.company_value/len(company.stocks))
            db.session.commit()


    if context.content.lower() == "currency_bot!":
        await context.channel.send("Hello, I am Currency Bot here are some commands: 'create_account!' to initiate your account, to see a current list of companies available message 'companies!', for your account's information message 'account!', to buy a stock in a company say 'buy_share! (quantity of shares) (company name)', and to sell a stock in a company say 'sell_share! (quantity of shares) (company name)', to create a company say 'create_company! (company's name)' you must have admin permissions for this command; message an admin to be added to the list of admins, to see a current list of users message 'users!', and to get commands to interact with the database say 'help_database!'")
        print("introduction called")

    elif context.content.lower() == "update_sim!":
        if context.author.name in admins:
            print("updating sim by command of: " + context.author.name)
            await context.channel.send("I am updating the simulation right now this may take awhile, you will not be able to buy or sell stock during this time.")
            stop = True
            for i in Company.query.all():
                for x in i.stocks:
                    x.value = str(int(i.company_value)/len(i.stocks))
            await context.channel.send("I have finished updateing the simulation, commands can now be made.")
            stop = False
        else:
            await context.channel.send("I am sorry but you don't have permission to do this, ask an admin to add you to the list of admins.")

    elif context.content.lower() == "create_account!" and stop == False:
        print("trying")
        #user check
        if not User.query.filter_by(discord_id=str(context.author.id)).first():
            user = User(discord_id=str(context.author.id), username=context.author.name)
            db.session.add(user)
            db.session.commit()
            await context.channel.send("Your account was created.")
            print("Succeeded to create account:success")
        else:
            await context.channel.send("You already have an account.")
            print("failed to create account:alreadyexist")


    elif context.content.lower().split(" ")[0] == "account!" and stop == False:
        if len(context.content.lower().split(" ")) == 2:
            if User.query.filter_by(username=str(context.content.split(" ")[1])).first():
                await context.channel.send(User.query.filter_by(username=str(context.content[1])).first())
                print("diplaying account of " + context.content.split(" ")[1])
            else:
                await context.channel.send("There is not account with that name.")
                print("failed to show account:noexist")
        else:
            if User.query.filter_by(discord_id=str(context.author.id)).first():
                await context.channel.send(User.query.filter_by(discord_id=str(context.author.id)).first())
                print("diplaying account of " + context.author.name)
            else:
                await context.channel.send("You dont have an account.")
                print("failed to show account:noexist")


    elif context.content.lower().split(" ")[0] == "change_name!" and stop == False:
        if len(context.content.split(" ")) == 1:
            if User.query.filter_by(discord_id=str(context.author.id)).first():
                User.query.filter_by(discord_id=str(context.author.id)).first().username = context.author.name
                db.session.commit()
                await context.channel.send("Your username was changed.")
                print("Changed the username")
            else:
                await context.channel.send("Sorry you dont have an account, you can make one with the command 'create_account!'.")
                print("failed to change the username:noexist")
        else:
            await context.channel.send("Your formmatting was wrong.")
            print("failed to change the username:formatting")


    elif context.content.lower() == "users!":
        await context.channel.send(User.query.all())
        print("showing all users at this time")

    elif context.content.lower() == "companies!":
        await context.channel.send(Company.query.all())
        print("showing all companies at this time")


    elif context.content.lower().split(" ")[0] == "create_company!" and stop == False:
        if len(context.content.split(" ")) == 2:
            if not Company.query.filter_by(company_name=context.content.split(" ")[1]).first():
                if context.author.name in admins:
                    company_1 = Company(company_name=context.content.split(" ")[1])
                    db.session.add(company_1)
                    db.session.commit()
                    await context.channel.send("A new company has been made.")
                    print("Succeeded to make company:success")
                else:
                    await context.channel.send("Sorry you don't have permission to do this.")
                    print("failed to make company:notadmin")
            else:
                await context.channel.send("Sorry there already is a company with that name.")
                print("failed to make company:alreadyexist")
        else:
            await context.channel.send("Sorry but the formatting you used is wrong.")
            print("failed to make company:formatting")


    elif context.content.lower().split(" ")[0] == "buy_share!" and stop == False:
        if len(context.content.split(" ")) == 3:
            try:
                quantity = int(context.content.split(" ")[1])
            except:
                await context.channel.send("You need to put a whole number(exp:'3') for the quantity.")
                print("failed to purchase stock:notquantity")
            if quantity <= 10:
                if User.query.filter_by(discord_id=context.author.id).first():
                    user = User.query.filter_by(discord_id=context.author.id).first()
                    company = Company.query.filter_by(company_name=context.content.split(" ")[2]).first()
                    if company:
                        def making_stock():
                            transaction = "nothing"
                            stock = Stock(value="0", state="sold", user_id=user.id, company_id=company.id)
                            try:
                                stock_price = len(company.stocks)
                            except:
                                stock_price = 0
                            stock.value = str(stock_price)
                            company.old_stock_number = len(company.stocks)
                            if int(user.money) >= stock_price*quantity and int(user.money) != 0:
                                user.money = str(int(user.money) - stock_price)
                                transaction = "You bought one share, Company: " + company.company_name + " Price: " + stock.value
                                db.session.add(stock)
                                db.session.commit()
                                company.company_value = stock_price*len(company.stocks)
                                db.session.commit()
                                print("Succeeded to purchase stock:success")
                                return transaction
                            else:
                                transaction = "Sorry you dont have enough money."
                                print("failed to purchase stock:notenoughmoney")
                                return transaction
                        for i in range(0, quantity):
                            await context.channel.send(making_stock())
                    else:
                        await context.channel.send("Sorry but that company does not exist.")
                        print("failed to purchase stock:nocompany")
                else:
                    await context.channel.send("Sorry but you don't have an account, make an account with the 'create_account!' command.")
                    print("failed to purchase stock:noaccount")
            else:
                await context.channel.send("Sorry but the transaction is too big, the maximum is 10.")
                print("failed to purchase stock:toobig")
        else:
            await context.channel.send("Sorry but the formmatting you used is wrong.")
            print("failed to purchase stock:formatting")


    elif context.content.lower().split(" ")[0] == "sell_share!" and stop == False:
        if len(context.content.split(" ")) == 3:
            try:
                quantity = int(context.content.split(" ")[1])
            except:
                await context.channel.send("You need to put an whole number(exp:'3') for the quantity.")
                print("failed to purchase stock:notquantity")
            if quantity < 10:
                if User.query.filter_by(discord_id=context.author.id).first():
                    user = User.query.filter_by(discord_id=context.author.id).first()
                    company = Company.query.filter_by(company_name=context.content.split(" ")[2]).first()
                    if company:
                        def selling_stock():
                            try:
                                transaction = "nothing"
                                #look for the stock
                                for i in user.stocks:
                                    if i.company_id == company.id:
                                        stock = i
                                        stock.value = str(len(company.stocks)-1)
                                        company.company_value = str(int(stock.value)*len(company.stocks))
                                        user.money = str(int(user.money) + int(stock.value))
                                        db.session.delete(stock)
                                        db.session.commit()
                                        break
                                company.old_stock_number = len(company.stocks)
                                transaction = "You sold one share, Company: " + company.company_name + " Price: " + stock.value
                                db.session.commit()
                                print("Succeeded to sell stock:success")
                                return transaction
                            except:
                                transaction = "Sorry you dont have enough shares."
                                print("failed to sell stock:notenoughstock")
                                return transaction
                        for i in range(0, quantity):
                            await context.channel.send(selling_stock())
                    else:
                        await context.channel.send("Sorry but that company does not exist.")
                        print("failed to purchase stock:nocompany")
                else:
                    await context.channel.send("Sorry but you don't have an account, make an account with the create_account! command.")
                    print("failed to purchase stock:noaccount")
            else:
                await context.channel.send("Sorry but the transaction is too big, there is a max of 10.")
                print("failed to purchase stock:toobig")
        else:
            await context.channel.send("Sorry but the formmatting you used is wrong.")
            print("failed to purchase stock:formatting")


    #database commmands


    elif context.content.lower() == "database_help!":
        if context.author.name in admins:
            if context.author.dm_channel:
                await context.author.dm_channel.send("Here are some database commands: to delete a user say 'delete_user! (the persons username)', to delete a company say 'delete_company (company name)', and to add an admin say 'add_admin! (the persons discord username without the numbers exp:'tamatoo')'")
                print("Succeeded to help admin:success")
            else:
                await context.author.create_dm()
                await context.author.dm_channel.send("Here are some database commands: to delete a user say 'delete_user! (the persons username)', to delete a company say 'delete_company (company name)', and to add an admin say 'add_admin! (the persons discord username without the numbers exp:'tamatoo')'")
                print("Succeeded to help admin:success")
        else:
            await context.channel.send("Sorry but you are not an admin, message an admin to become an admin.")
            print("failed to help admin:notadmin")

    elif context.content.lower().split(" ")[0] == "delete_user!":
        if context.author.name in admins:
            if len(context.content.lower().split(" ")) == 2:
                user = User.query.filter_by(username=context.content.split(" ")[1]).first()
                if user:
                    for i in user.stocks:
                        db.session.delete(i)
                    db.session.delete(user)
                    db.session.commit()
                    await context.channel.send("I have deleted that user.")
                    print("Succeeded to delete user:success")
                else:
                    await context.channel.send("Sorry but the user you entered does not exist.")
                    print("failed to delete user:noexist")
            else:
                await context.channel.send("Sorry but the formmatting you used is wrong.")
                print("failed to delete user:wrongformatt")
        else:
            await context.channel.send("Sorry but you are not an admin, message an admin to become an admin.")
            print("failed to delete user:notadmin")


    elif context.content.lower().split(" ")[0] == "delete_company!":
        if context.author.name in admins:
            if len(context.content.lower().split(" ")) == 2:
                company = Company.query.filter_by(company_name=context.content.split(" ")[1]).first()
                if company:
                    for i in company.stocks:
                        db.session.delete(i)
                    db.session.delete(company)
                    db.session.commit()
                    await context.channel.send("I have deleted that company.")
                    print("Succeeded to delete user:success")
                else:
                    await context.channel.send("Sorry but the company you entered does not exist.")
                    print("failed to delete company:noexist")
            else:
                await context.channel.send("Sorry but the formmatting you used is wrong.")
                print("failed to delete company:wrongformatt")
        else:
            await context.channel.send("Sorry but you are not an admin, message an admin to become an admin.")
            print("failed to delete company:notadmin")

    elif context.content.lower().split(" ")[0] == "add_admin!":
        if context.author.name in admins:
            if len(context.content.lower().split(" ")) == 2:
                admins.append(context.content.split(" ")[1])
                await context.channel.send("I have added that discord name to the list of admins.")
                print("Succeeded to add admin:success")
            else:
                await context.channel.send("Sorry but the formmatting you used is wrong.")
                print("failed to add admin:wrongformatt")
        else:
            await context.channel.send("Sorry but you are not an admin, message an admin to become an admin.")
            print("failed to add admin:notadmin")

client.run("NDg4MDIzNDA0NjE2NjEzOTAz.XZkR9w.Q62a4Q3L7nsNDj4nY4C8PZ4w9qI")
#cd C:\Users\shakeandbakeforever\gitcolabstuff\colabstuff
