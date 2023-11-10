# Mastermind Game
#### Video Demo: https://youtu.be/kRCyFzgw_Xg
#### Description: Guess the colors and be the top scorer player!


## Helpers.py

- Create engine that connects database and SQLite as dialect
- Create class that mapped to table in database
- Sets scores for each gamemode
- Render custom apology message (error message)
- Formatting gamemode to be used as filter in Jinja
- Calculate scores based on gamemode and number of guess
- Sets each gamemode to store in database
- Decorate routes to require login

## Register

User needs to create an account to start playing.

There are 4 fields to be filled:
1. Username
2. Name
3. Password
4. Confirm Password

Username must be **unique**.

Password must be at least **8 characters long** which includes **one uppercase**, **one lowercase**, **one digit** and **one symbol** from **#?!@$%^&*-**.

Password and confirm password must be the same.

Apology message will be shown if user didn't follow the requirements.

## Log In

User enter username and password to log in.

If the username doesn't exist or password doesn't match the username, an apology message will be prompted.

## How To Play?

Shows the rules of the game and scores for each gamemode.

User may choose to skip reading and continue to Gamemode page or start playing the game.

## Play

The game will generate a random sequence of color as question and user have to guess it. The sequence will be based on the gamemode user has chosen.

The game generates different number of pins for question, answer and check based on the number of pins user set in gamemode.

By default, the gamemode is set to **4 pins - Normal** mode (which means no duplication of colors in the sequence).

User needs to drag and drop color pins to fill the answer pins. After filling all answer pins with color pins, user will only able to click on **Check** button.

The game will reveals small green pins if correct color and correct position is submitted and small red pins if correct color but incorrect position after clicking **Check** button.

User wins if all colors and positions are guessed correctly within 10 tries. Else, user need to try again.

User's scores will then be calculated based on gamemode and number of guesses.

There's a **New Game** button for user to start a new game.

Every time user wants to leave the game, close current tab or close the browser, the browser will prompt a confirmation.

## Gamemode

A selection of number of pins for user to choose - 4, 6 and 8 pins.

Duplication is toggleable. When it is toggled on, there might be repeated color appears in the game sequence.

There are 6 gamemodes in total:
1. 4 pins - Normal
2. 4 pins - Duplicate
3. 6 pins - Normal
4. 6 pins - Duplicate
5. 8 pins - Normal
6. 8 pins - Duplicate

User will be redirected to start playing game after clicking on **Save** button. User's choice of gamemode will be remembered until changes are made.

Gamemode is set to **4 pins - Normal** when user logged in or newly registered.

## Leaderboard

Leaderboard shows top 10 players with most scores overall and top 10 players with most scores for each gamemode. Total win game and best game played for each gamemode are shown too.

## Game History

Latest 10 game history will be shown including the gamemode, scores, guess, and played time.

## Personal Best

User's personal best will be recorded based on each gamemode. It will automatically update if user surpasses previous best record.

## Edit Profile

User get to edit name or change to a new password.
