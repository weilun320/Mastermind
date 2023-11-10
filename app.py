import re

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import func
from sqlalchemy.orm import Session as Sess
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import (
    apology,
    gamemode,
    get_score,
    init_gamemode,
    login_required,
    User,
    Gamemode,
    Leaderboard,
    engine,
    Base,
    NORMAL,
    DUPLICATE,
)

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["gamemode"] = gamemode

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create tables to database
Base.metadata.create_all(engine)

# Adding gamemodes to database
with Sess(engine) as sess:
    rows = sess.query(Gamemode).all()

    if not rows:
        for gamemode in init_gamemode():
            sess.add(gamemode)
            sess.commit()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/best")
@login_required
def best():
    """Show personal best game played of user"""

    # Bound SQLAlchemy Session to engine to interact with database
    with Sess(engine) as sess:
        best = []

        # Query database for the best game played by user for each gamemodes
        for gamemode in init_gamemode():
            row = (
                sess.query(
                    Leaderboard.scores,
                    Leaderboard.guess,
                    Leaderboard.played,
                    Gamemode.id,
                )
                .select_from(Leaderboard)
                .join(Gamemode)
                .filter(
                    Gamemode.pins == gamemode.pins,
                    Gamemode.duplicate == gamemode.duplicate,
                    Leaderboard.user_id == session["user_id"],
                )
                .order_by(Leaderboard.guess)
                .first()
            )

            if row:
                best.append(row)

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("best.html", best=best)


@app.route("/gamemode", methods=["GET", "POST"])
@login_required
def gamemode():
    """Sets gamemode"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure user selected number of pins for gamemode
        if not request.form.get("pins"):
            return apology("please select number of pins to play")
        # Ensure the selected pins is either 4, 6 or 8
        elif not request.form.get("pins") in ["4", "6", "8"]:
            return apology("invalid number of pins")

        # Check for user switched on duplicate mode
        if request.form.get("duplicate") == "duplicate":
            # Remember user's choice for duplication
            session["game_duplicate"] = "duplicate"
        # Remove duplicate from session if user switched off
        elif not request.form.get("duplicate") == "duplicate":
            if "game_duplicate" in session:
                session.pop("game_duplicate", None)

        # Remember user's choice for number of pins
        session["game_pins"] = request.form.get("pins")

        # Redirect user to start playing game
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("gamemode.html")


@app.route("/history")
@login_required
def history():
    """Show game history"""

    # Bound SQLAlchemy Session to engine to interact with database
    with Sess(engine) as sess:
        # Query database for the last 10 game played by user
        history = (
            sess.query(
                Leaderboard.scores,
                Leaderboard.guess,
                Leaderboard.played,
                Gamemode.pins,
                Gamemode.duplicate,
            )
            .select_from(Leaderboard)
            .join(Gamemode)
            .join(User)
            .filter(User.id == session["user_id"])
            .order_by(Leaderboard.played.desc())
            .limit(10)
            .all()
        )

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("history.html", history=history)


@app.route("/howtoplay")
@login_required
def howtoplay():
    """Show instructions and scores for each gamemodes"""

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("howtoplay.html")


@app.route("/")
@login_required
def index():
    """Mastermind game"""

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("index.html")


@app.route("/leaderboard")
@login_required
def leaderboard():
    """Show top player and leaderboard for each gamemode"""

    # Bound SQLAlchemy Session to engine to interact with database
    with Sess(engine) as sess:
        # Query database for top 10 best game played for "4 pins - Nomal" mode
        normal_4 = (
            sess.query(
                User.name,
                func.sum(Leaderboard.scores).label("scores"),
                func.min(Leaderboard.guess).label("guess"),
                func.count(Leaderboard.user_id).label("count"),
            )
            .select_from(User)
            .join(Leaderboard)
            .join(Gamemode)
            .filter(Gamemode.pins == 4, Gamemode.duplicate == False)
            .order_by(func.sum(Leaderboard.scores).desc(), Leaderboard.guess, User.name)
            .group_by(User.id)
            .limit(10)
            .all()
        )

        # Query database for top 10 best game played for "6 pins - Nomal" mode
        normal_6 = (
            sess.query(
                User.name,
                func.sum(Leaderboard.scores).label("scores"),
                func.min(Leaderboard.guess).label("guess"),
                func.count(Leaderboard.user_id).label("count"),
            )
            .select_from(User)
            .join(Leaderboard)
            .join(Gamemode)
            .filter(Gamemode.pins == 6, Gamemode.duplicate == False)
            .order_by(func.sum(Leaderboard.scores).desc(), Leaderboard.guess, User.name)
            .group_by(User.id)
            .limit(10)
            .all()
        )

        # Query database for top 10 best game played for "8 pins - Nomal" mode
        normal_8 = (
            sess.query(
                User.name,
                func.sum(Leaderboard.scores).label("scores"),
                func.min(Leaderboard.guess).label("guess"),
                func.count(Leaderboard.user_id).label("count"),
            )
            .select_from(User)
            .join(Leaderboard)
            .join(Gamemode)
            .filter(Gamemode.pins == 8, Gamemode.duplicate == False)
            .order_by(func.sum(Leaderboard.scores).desc(), Leaderboard.guess, User.name)
            .group_by(User.id)
            .limit(10)
            .all()
        )

        # Query database for top 10 best game played for "4 pins - Duplicate" mode
        duplicate_4 = (
            sess.query(
                User.name,
                func.sum(Leaderboard.scores).label("scores"),
                func.min(Leaderboard.guess).label("guess"),
                func.count(Leaderboard.user_id).label("count"),
            )
            .select_from(User)
            .join(Leaderboard)
            .join(Gamemode)
            .filter(Gamemode.pins == 4, Gamemode.duplicate == True)
            .order_by(func.sum(Leaderboard.scores).desc(), Leaderboard.guess, User.name)
            .group_by(User.id)
            .limit(10)
            .all()
        )

        # Query database for top 10 best game played for "6 pins - Duplicate" mode
        duplicate_6 = (
            sess.query(
                User.name,
                func.sum(Leaderboard.scores).label("scores"),
                func.min(Leaderboard.guess).label("guess"),
                func.count(Leaderboard.user_id).label("count"),
            )
            .select_from(User)
            .join(Leaderboard)
            .join(Gamemode)
            .filter(Gamemode.pins == 6, Gamemode.duplicate == True)
            .order_by(func.sum(Leaderboard.scores).desc(), Leaderboard.guess, User.name)
            .group_by(User.id)
            .limit(10)
            .all()
        )

        # Query database for top 10 best game played for "8 pins - Duplicate" mode
        duplicate_8 = (
            sess.query(
                User.name,
                func.sum(Leaderboard.scores).label("scores"),
                func.min(Leaderboard.guess).label("guess"),
                func.count(Leaderboard.user_id).label("count"),
            )
            .select_from(User)
            .join(Leaderboard)
            .join(Gamemode)
            .filter(Gamemode.pins == 8, Gamemode.duplicate == True)
            .order_by(func.sum(Leaderboard.scores).desc(), Leaderboard.guess, User.name)
            .group_by(User.id)
            .limit(10)
            .all()
        )

        # Query database for top 10 highest score player
        top = (
            sess.query(User.name, User.scores)
            .filter(User.scores > 0)
            .order_by(User.scores.desc(), User.name)
            .limit(10)
            .all()
        )

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template(
        "leaderboard.html",
        normal_4=normal_4,
        normal_6=normal_6,
        normal_8=normal_8,
        duplicate_4=duplicate_4,
        duplicate_6=duplicate_6,
        duplicate_8=duplicate_8,
        top=top,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user's details and preferences
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("missing username")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("missing password")

        # Bound SQLAlchemy Session to engine to interact with database
        with Sess(engine) as sess:
            # Query database for user
            rows = (
                sess.query(User)
                .filter(User.username == request.form.get("username"))
                .first()
            )

        # Ensure user has an account and password is correct
        if not rows or not check_password_hash(rows.hash, request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows.id
        session["user_name"] = rows.name
        session["game_pins"] = "4"

        flash("Login Successfully!")
        # Redirect user to instruction page
        return redirect("/howtoplay")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user's details and preferences
    session.clear()

    # User reached route via GET (as by clicking a link or via redirect)
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Edit user profile"""

    # Bound SQLAlchemy Session to engine to interact with database
    with Sess(engine) as sess:
        # Query database for user's details
        user = sess.query(User).filter(User.id == session["user_id"]).first()

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":
            changes = False

            # Check if user has submitted a new name
            if request.form.get("name") and not request.form.get("name") == user.name:
                # Set new name
                user.name = request.form.get("name")
                changes = True

            # Check if user has submitted old password
            if request.form.get("password"):
                # Ensure new password was submitted
                if not request.form.get("new"):
                    return apology("missing new password")
                # Ensure confirm new password was submitted
                elif not request.form.get("confirm"):
                    return apology("missing confirm new password")
                # Ensure old password is valid
                elif not check_password_hash(user.hash, request.form.get("password")):
                    return apology("invalid old password")
                # Ensure new password and confirm new password is the same
                elif not request.form.get("new") == request.form.get("confirm"):
                    return apology(
                        "new password and confirm new password must be the same"
                    )
                # Ensure new password is at least 8 characters long, contains 1 uppercase, 1 lowercase, 1 number, 1 symbol from #?!@$%^&*-
                elif re.search(
                    r"^(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[#?!@$%^&*-]).{8,}$",
                    request.form.get("new"),
                ):
                    # Set new password
                    user.hash = generate_password_hash(request.form.get("new"))
                    changes = True
                # User submitted new password that didn't meet the requirement
                else:
                    return apology(
                        "passwords must be at least 8 characters long, password must contain at least one digit, one uppercase, one lowercase, one symbol from #?!@$%^&*-"
                    )
            # User didn't submit old password but submitted new password and/or confirm new password
            elif not request.form.get("password"):
                if request.form.get("new") or request.form.get("confirm"):
                    return apology("missing old password")

            # Check for any changes
            if changes:
                # Update user_name to new name for session
                session["user_name"] = user.name
                # Flush pending changes
                sess.commit()

                flash("Updated Successfully!")
                # Redirect user to instruction page
                return redirect("/howtoplay")

            # Redirect user to start playing game
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("profile.html", user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("missing username")
        # Ensure name was submitted
        elif not request.form.get("name"):
            return apology("missing name")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("missing password")
        # Ensure confirm password was submitted
        elif not request.form.get("confirm"):
            return apology("missing confirm password")

        # Bound SQLAlchemy Session to engine to interact with database
        with Sess(engine) as sess:
            # Query database for username
            users = (
                sess.query(User)
                .filter(User.username == request.form.get("username"))
                .first()
            )

            # Ensure username doesn't exist
            if users:
                return apology("username has been taken")
            # Ensure password and confirm password is the same
            elif not request.form.get("password") == request.form.get("confirm"):
                return apology("password and confirm password must be the same")

            # Ensure password is at least 8 characters long, contains 1 uppercase, 1 lowercase, 1 number, 1 symbol from #?!@$%^&*-
            if re.search(
                r"^(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[#?!@$%^&*-]).{8,}$",
                request.form.get("password"),
            ):
                # Create an user object
                user = User(
                    username=request.form.get("username"),
                    name=request.form.get("name"),
                    hash=generate_password_hash(request.form.get("password")),
                )
            # User submitted password that didn't meet the requirement
            else:
                return apology(
                    "passwords must be at least 8 characters long, password must contain at least one digit, one uppercase, one lowercase, one symbol from #?!@$%^&*-"
                )

            # Add new user to database
            sess.add(user)
            # Flush pending changes
            sess.commit()

            # Query database for newly added user
            users = sess.query(User).filter(User.username == user.username).first()
            if users:
                # Remember which user registered
                session["user_id"] = users.id
                session["user_name"] = users.name

        flash("Registered Successfully!")
        # Redirect user to instruction page
        return redirect("/howtoplay")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("register.html")


@app.route("/win", methods=["GET", "POST"])
@login_required
def win():
    """User wins a game"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure duplicate, pins and guess was submitted
        if (
            not request.form.get("duplicate")
            or not request.form.get("pins")
            or not request.form.get("guess")
        ):
            return apology("invalid submission")
        # Ensure duplicate is either true or false
        elif not request.form.get("duplicate") in ["true", "false"]:
            return apology("invalid duplication type")
        # Ensure pins is either 4, 6 or 8
        elif not request.form.get("pins") in ["4", "6", "8"]:
            return apology("invalid pins type")
        # Ensure guess is a digit and between 1 to 10 inclusive
        elif not request.form.get("guess").isdecimal() or not int(
            request.form.get("guess")
        ) in range(1, 11):
            return apology("invalid guesses")

        # Bound SQLAlchemy Session to engine to interact with database
        with Sess(engine) as sess:
            # If duplicate is true
            if request.form.get("duplicate") == "true":
                # Query database for gamemode with submitted pins and duplicate
                gamemodes = (
                    sess.query(Gamemode)
                    .filter(
                        Gamemode.pins == int(request.form.get("pins")),
                        Gamemode.duplicate == True,
                    )
                    .first()
                )
            # If duplicate is false
            else:
                # Query database for gamemode with submitted pins and duplicate
                gamemodes = (
                    sess.query(Gamemode)
                    .filter(
                        Gamemode.pins == int(request.form.get("pins")),
                        Gamemode.duplicate == False,
                    )
                    .first()
                )

            # Ensure gamemode is valid
            if gamemodes:
                # Get score based on gamemode and number of guess
                score = get_score(
                    gamemodes.pins, gamemodes.duplicate, int(request.form.get("guess"))
                )

                # Create a leaderboard object
                leaderboard = Leaderboard(
                    user_id=session["user_id"],
                    gamemode_id=gamemodes.id,
                    scores=score,
                    guess=int(request.form.get("guess")),
                )

                # Query for user
                user = sess.query(User).filter(User.id == session["user_id"]).first()

                # Update user's score
                user.scores = user.scores + score

                # Add leaderboard to database
                sess.add(leaderboard)
                # Flush pending changes
                sess.commit()

                # Redirect user to game history
                return redirect("/history")
            # Invalid gamemode was submitted
            else:
                return apology("invalid gamemode")

    # User reached route via GET (as by clicking a link or via redirect)
    return redirect("/")
