# Telegram Score Bot (Python)

**This was my first Telegram Bot as a beginner, so it has fairly poor practices/modularity. Please feel free to make your own improvements to it.**



This is a simple Telegram Bot that helps to manage scores of different groups. The provided code works for **4 groups**, but you can modify this in the code yourself based on your needs.

If you're running your own challenge/quiz on Telegram and need a way to manage the scores of different groups, this bot can help with that. 



`/score`

- Displays a list of the current scores

  ![scoreCommand](https://github.com/caydennn/Telegram-Score-Bot/blob/master/Images/scoreCommand.jpg?raw=true)

`/updateScores`

Only for moderators that can login with their passwords

![updateScoresCommand](https://github.com/caydennn/Telegram-Score-Bot/blob/master/Images/updateScoresCommand.jpg?raw=true)

You can add this bot to a main group so that participants can check their scores anytime with `/score`.

Private message the bot `/updatescores` to update the scores so that the participants do not see the password for moderators (if not they can play around with their own group scores)

This repo only provides the code covering the PgSQL and Telegram code portion, but doesn't fully cover Heroku deployment.

## Getting started

Before running the code, you'll need the following:

- A PostGres SQL Account
- Telegram Bot API (From BotFather)



### Setting up PostGreSQL with Heroku

You'll need to set up PostGresSQL before anything else.

If you want to set up PgSQL programmatically, do check out this [video](https://www.youtube.com/watch?v=i04Rgnn2XbI).

#### Setting up database

This is a great [article](https://medium.com/@vapurrmaid/getting-started-with-heroku-postgres-and-pgadmin-run-on-part-2-90d9499ed8fb) to find out how to set up your database with Heroku and PostgreSQL.  Make sure to note down your:

1) DB_NAME

2) DB_USER

3) DB_PASS

4) DB_HOST

5) DB_PORT

as they'll be used in the code.



Once that is done, create a Table under your database called **scores**. 

![scoresTable](https://github.com/caydennn/Telegram-Score-Bot/blob/master/Images/scoresTable.png?raw=true)

Create 2 **columns** with the corresponding values: 

- **ID** (Integer) -> 1
- **Info** (Json ) -> `{"G1": 0, "G2": 0, "G3": 0,  "G4": 0}`

<img src="https://github.com/caydennn/Telegram-Score-Bot/blob/master/Images/columnHeaders.png?raw=true" alt="scoresHeaders"  />

<img src="https://github.com/caydennn/Telegram-Score-Bot/blob/master/Images/columnValues.png?raw=true" alt="columnValues" style="zoom:150%;" />

And that should be fine. 



## Running the code

Before running the code, do run:

`pip install requirements.txt`

to make sure you have the required dependencies. 

(There are unfortunately some extra modules that are included by accident but I haven't gotten around to finding out which they are yet. Oops. But this shouldn't affect things too much.)



### Modifying the variables

You need to modify the following variables in your own bot:



**SQL PORTION**

1) DB_NAME

2) DB_USER

3) DB_PASS

4) DB_HOST

5) DB_PORT (only if its different from 5432)



**TELEGRAM PORTION**

1) Passwords (To access the update score function)

2) Telegram Token (This is under the function main())



*! Do NOT use this code structure in production!* 

It is advisable to save your sensitive information in a env file and reference the variables from there.





# FAQ

 <u>**What if I have more than 4 groups?**</u> 

**In your SQL Table,** you'll need to add 'G5', 'G6' and so on in your **info** json.



**Under the Telegram Code Portion,** you'll need to modify the:

- group_keyboard

  ```python
  group_keyboard = [['G1', 'G2'],
                    ['G3', 'G4'],
                    ['Done']]
  ```

  can be modified to:

  ```python
  group_keyboard = [['G1', 'G2'],
                    ['G3', 'G4'],
                    ['G5', 'G6'],
                    #...
                    ['Done']]
  ```

  and so on. 

- Scoreboard (Under get_score)

  ``` python
  scoreboard = """
  Group 1: {G1}
  Group 2: {G2}
  Group 3: {G3}
  Group 4: {G4}
  Group 5: {G5}
  Group 6: {G6}
  
  # Add the extra groups here
  DON'T GIVE UP!
      """.format(**data)
  ```

- Under main() -> conv_handler -> states -> CHOOSINGGROUPING:

  ```python
  CHOOSINGGROUPING: [MessageHandler(Filters.regex('^(G1|G2|G3|G4)$'), action),
                                  MessageHandler(Filters.regex('^(Done)$'), cancel)],
  ```

  You'll need to change: `^(G1|G2|G3|G4)$` to include the additional groups. For example, `^(G1|G2|G3|G4|G5|G6)$`

  

<u>**How do I deploy this code on Heroku?**</u>

You can find a great article about this [here](https://towardsdatascience.com/how-to-deploy-a-telegram-bot-using-heroku-for-free-9436f89575d2). 