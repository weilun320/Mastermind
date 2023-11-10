from flask import redirect, render_template, session
from functools import wraps
from sqlalchemy import create_engine, func, Boolean, Column, ForeignKey, Index, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

# Create engine that connects to database and SQLite as dialect together
engine = create_engine("sqlite:///mastermind.db", echo=True)

# A base class that stores classes and mapped tables
Base = declarative_base()

# User's class that mapped to "users" table followed by names and datatypes of columns
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    name = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    scores = Column(Integer, nullable=False, default=0)
    Index("username", username, unique=True)

# Gamemode's class that mapped to "gamemodes" table followed by names and datatypes of columns
class Gamemode(Base):
    __tablename__ = "gamemodes"

    id = Column(Integer, primary_key=True)
    pins = Column(Integer, nullable=False)
    duplicate = Column(Boolean, nullable=False)

# Leaderboard's class that mapped to "leaderboards" table followed by names and datatypes of columns
class Leaderboard(Base):
    __tablename__ = "leaderboards"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gamemode_id = Column(Integer, ForeignKey("gamemodes.id"), nullable=False)
    scores = Column(Integer, nullable=False)
    guess = Column(Integer, nullable=False)
    played = Column(DateTime, server_default=func.now())


# Scoring for non-duplicate gamemode
NORMAL = {
    4: {
        10: [1, 2],
        8: [3, 4],
        6: [5, 6],
        4: [7, 8],
        2: [9, 10]
    },
    6: {
        20: [1, 2],
        16: [3, 4],
        12: [5, 6],
        8: [7, 8],
        4: [9, 10]
    },
    8: {
        30: [1, 2],
        24: [3, 4],
        18: [5, 6],
        12: [7, 8],
        8: [9, 10]
    }
}

# Scoring for duplicate gamemode
DUPLICATE = {
    4: {
        20: [1, 2],
        16: [3, 4],
        12: [5, 6],
        8: [7, 8],
        4: [9, 10]
    },
    6: {
        30: [1, 2],
        24: [3, 4],
        18: [5, 6],
        12: [7, 8],
        8: [9, 10]
    },
    8: {
        50: [1, 2],
        40: [3, 4],
        30: [5, 6],
        20: [7, 8],
        10: [9, 10]
    }
}


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen
        """
        special = [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"), ("&", "~a"), ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]

        for old, new in special:
            s = s.replace(old, new)

        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def gamemode(id):
    """Format gamemode id"""
    match(id):
        case 1:
            return "4 pins - Normal"
        case 2:
            return "4 pins - Duplicate"
        case 3:
            return "6 pins - Normal"
        case 4:
            return "6 pins - Duplicate"
        case 5:
            return "8 pins - Normal"
        case 6:
            return "8 pins - Duplicate"


def get_score(pin, duplicate, guess):
    """Get score based on gamemode and number of guess"""
    if duplicate:
        for pins in DUPLICATE:
            if pin == pins:
                scores = DUPLICATE[pins]
                for score in scores:
                    if guess in scores[score]:
                        return score
    else:
        for pins in NORMAL:
            if pin == pins:
                scores = NORMAL[pins]
                for score in scores:
                    if guess in scores[score]:
                        return score


def init_gamemode():
    """Sets gamemode"""
    gamemode_list = []
    for n in range(4, 9, 2):
        gamemode_list.append(Gamemode(pins = n, duplicate = False))
        gamemode_list.append(Gamemode(pins = n, duplicate = True))

    return gamemode_list


def login_required(f):
    """
    Decorate routes to require login
    https://flask.palletsprojects.com/en/3.0.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
