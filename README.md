# CS50 Final Project - TODO task

#### Video Demo:  https://www.youtube.com/watch?v=MMZkQUfUDps

#### Description:
The project is a web page where you register tasks to be done. The implementation is quite simple, to keep the project scope under control. I wanted to do a project like this to expand my knowledge of Flask and the web in general, mainly because this was a gap I had.

Technologies used:
- SQL
- Python
- Jinja
- libraries and packages

For the page to be standard, a base page and a style file were used. Bootstrap was also used to facilitate the creation of screen layouts.

## How the webpage works:
The user need to register yourself. During registration you need to enter these fields:
- Name
- Username: it is check if already exist a user with de same name. Only lowercase characters are accepted. Numbers and symbols are not allowed.
- Password: it is checked to match.

After registration, the user is logged in automatically.
For new access just login. Username and password are always validated.

After login the main screen opens, on it you will find the date and all tasks related to that date and logged in user.
On this screen you can:
- register new tasks -- in the option "Nova Tarefa" you register all tasks for today or for another date. A new screen will open for this registration with two fields: task name and date. The date will already be suggested the date that was being visualized on the main screen. Tasks will always be added to the end of the list.;
- prioritize tasks -- Up the task in the list. Important: the tasks done are considered;
- deprioritize tasks -- Down the task in the list. Important: the tasks done are considered;
- mark as done -- finishes the task by getting crossed out on the screen;
- mark as not done -- reopens the task, removing the crossed out on the screen;
- delete tasks -- will permanently delete the task from the database;
- edit tasks -- In this option you can edit the date or the name of the task. Will open the same screen as the "Nova Tarefa" with the data already filled in;
- check other days' task -- you can browse between the dates;
- view only undone tasks;
- view all tasks per day.

Clicking on the "TODO" icon, which is in the header, you will be redirected to today's tasks.

All options are within this main screen. Several icons with images were used to make it more intuitive and simple to use.
Each user will be able to view only their tasks. For this reason there is the registration of users.

To exit the web page just go to the "log out" option at the page header.

### Routing:
Each route checks if the user is authenticated.
Once logged in you will remain logged in, internally who is using the web page is saved.

### Database:
Database stores all users and tasks. Important: The password is saved in hashed database to improve website security.
The table 'tarefas' uses foreign keys to relate users.