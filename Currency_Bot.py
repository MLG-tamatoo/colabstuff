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
    if context.content.lower() == "currency_bot!":
        await context.channel.send("Hello, I am Currency Bot here are some commands: 'Create Account!' to initiate your account, 'stock stats!' for the current prices of the stocks, for your account's information message 'my account', To buy a stock in a company say 'buy (amount of stock) (company name)', and To sell a stock in a company say 'sell (amount of stock) (company name)'")
        print("introduction called")


    elif context.content.lower() == "create_account!":
        print(type(context.author.id))
        print("trying")
        #user check
        if not User.query.filter_by(discord_id=str(context.author.id)).first():
            user = User(discord_id=str(context.author.id), username=context.author.name)
            db.session.add(user)
            db.session.commit()
            await context.channel.send("Your account was created.")
            print("account created")
        else:
            await context.channel.send("You already have an account. To get out of debt contact Tamatoo.")
            print("failed to create account")


    elif context.content.lower().split(" ")[0] == "account!":
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


    elif context.content.lower().split(" ")[0] == "change_name!":
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
            await context.channel.send("Please check formatting")
            print("failed to change the username:formatting")


    elif context.content.lower() == "users!":
        await context.channel.send(User.query.all())
        print("showing all users at this time")

    elif context.content.lower() == "companies!":
        await context.channel.send(Company.query.all())
        print("showing all companies at this time")


    elif context.content.lower().split(" ")[0] == "create_company!":
        if len(context.content.split(" ")) == 2:
            if not Company.query.filter_by(company_name=context.content.split(" ")[1]).first():
                if context.author.name == "tamatoo":
                    company_1 = Company(company_name=context.content.split(" ")[1])
                    db.session.add(company_1)
                    db.session.commit()
                    await context.channel.send("New company has been made.")
                    print("Succeeded to make company:success")
                else:
                    await context.channel.send("Sorry you don't have permission to do this.")
                    print("failed to make company:nopermission")
            else:
                await context.channel.send("Sorry there already is a company with that name.")
                print("failed to make company:alreadyexist")
        else:
            await context.channel.send("Sorry but the formatting you used is wrong.")
            print("failed to make company:formatting")


    elif context.content.lower().split(" ")[0] == "buy_stock!":
        if len(context.content.split(" ")) == 3:
            quantity = int(context.content.split(" ")[2])
            if quantity < 10:
                if User.query.filter_by(discord_id=context.author.id).first():
                    user = User.query.filter_by(discord_id=context.author.id).first()
                    company = Company.query.filter_by(company_name=context.content.split(" ")[1]).first()
                    if company:
                        def makeing_stock():
                            transaction = "nothing"
                            stock = Stock(value="0", state="sold", user_id=user.id, company_id=company.id)
                            if int(company.old_stock_number) == 0:
                                stock_price = 1
                            else:
                                stock_price = len(company.stocks)/int(company.old_stock_number)
                            company.company_value = stock_price*len(company.stocks)
                            stock.value = str(stock_price)
                            company.old_stock_number = len(company.stocks)
                            if int(user.money) >= stock_price*quantity and int(user.money) != 0:
                                user.money = str(int(user.money) - int(stock.value))
                                db.session.add(stock)
                                db.session.commit()
                                print("Succeeded to purchase stock:success")
                                transaction = "You bought one stock, good luck."
                                return transaction
                            else:
                                transaction = "Sorry you dont have enough money."
                                print("failed to purchase stock:notenoughmoney")
                                return transaction
                        for i in range(0, int(context.content.split(" ")[2])):
                            await context.channel.send(makeing_stock())
                    else:
                        await context.channel.send("Sorry but that company does not exist.")
                        print("failed to purchase stock:nocompany")
                else:
                    await context.channel.send("Sorry but you don't have an account, make an account with the create_account! command.")
                    print("failed to purchase stock:noaccount")
            else:
                await context.channel.send("Sorry but the transaction is too big.")
                print("failed to purchase stock:toobig")
        else:
            await context.channel.send("Sorry but you need to have the quantity be a number")
            print("failed to purchase stock:formatting")


client.run("NDg4MDIzNDA0NjE2NjEzOTAz.DndQBQ.V4w8jjvBEVRTD4behMPyPi5GPeE")
#cd C:\Users\shakeandbakeforever\Discord_Bots
