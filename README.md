
# The Logger 
### video link : https://youtu.be/ApgFd1DUJwQ
### DESCRIPTION: My project is a web app that students can use for tracking their study hours, track their courses and analyze and improve their study habits and also the stopwatch and audio enables students to focus.


Description: Studying can be seen hard and boring for most people who doesn't have self-discipline. The reason I built this app is  while I was studying for CS50 course, I tried to keep my study dates, study hours, courses i want to do later  in order to maintain persistance.But the problem was it was getting difficult to do it myself after certain time. And therefore I though this app would be useful to me and many people who want to self-study systematically while keeping track of their process. Also another problem this app solves is that for people who has hard time studying due to focus, or people who never enjoyed studying before;  the white noise, stopwatch, charts and session helps to solve that focus problem and also app encourages  motivation and self-discipline.The features includes user accounts, course management , study sessions, stopwatch, visual charts, export for downloading as CSV or JSON, dark mode toggle, white noise player.




File explanations:
-'app.py': The main Flask application containing all routes 
-'templates/': HTML files for login, dashboard, stopwatch, navbar and dashboard.
-'static/script.js': stopwatch, audio 
-'static/style.css': styles for minimal modern focus oriented interface.
-'README.md' : This document

Reasoning behind design choices:
- Flask for backend and routing, templates.
- SQL for database
- HTML5, CSS3 and JS for Frontend.
-Flask sessions and password for authentication
- localStorage for persistent client-side stopwatch 
-Audio and stopwatch runs independently, without restarting. It can be used as user wants.
- fonts and colors are chosen to create a futuristic modern userface and be less distracting.

Notes:
- Focused on user experince
- Charts can help displaying progress and keep the user motivated.
- Login/register system uses Flask messages for feedback. 


-- Installation
1 - clone the repository

2 - Install dependencies:
3 -  Inıtialize the database 
 4 - run the FLASK app

 open 'http://127.0.0.1:5000 in your browser.
-- Instructions 
1 - register to create an account 
2 - add courses
3 - log study sessions and hours 
4 - optionaly when studying use the chrometer, turn on the audio or turn the dark mode for less distraction which are all in the navbar.
5- After logging sessions view charts to see study progress.
6- optionalyl export data 

--challenges 
Some of the difficult tasks was:
to make the stopwatch consistent and visible throughout all pages but later it is discarded.
- making the audio not stop and continue where it left off to not make it noticable, this is still left noticable.
- The stopwatch was restarting when site gets reloaded, or jumping , this issue is solved.
-
--Improvement that can be done:
-A place to downloaded pdf, or lecture notes for each course and user can modify them.
- more motivational messsages in stopwatch or or dashboard,  a productivity score.
- A task list in the navbar to record the skills or other things that completed.
- an ai tool to give recommendation for courses,skills that user can benefit from. 
-more  moving icons or animations that appears when clicking on 
- an icon for the app
- pomodoro or user's time choice that can be opened as  a mode in the stopwatch
- more audio noises like lofi, or other.

Credits 
with the help of CS50 and CS50w lectures and ChatGPT

