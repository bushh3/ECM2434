# ECM2434 - Green Campus
## Project Overview
**Green Campus** is a **Django Web application** that uses **gamification mechanisms** to engage users in sustainability activities such as garbage collection, green travel, and environmental knowledge competitions. This system includes task system, points reward, ranking, location check-in (QR code/GPS) and other functions to encourage users to actively participate in sustainable development, develop environmental habits, and jointly build an environmentally friendly campus.

## Technology Stack
This project is built using the following technologies:
### Frontend
 **HTML**, **CSS**, **JavaScript**
### Backend
 **Django**, **Django REST Framework**
### Database
 **SQLite**
### API Design
 **RESTful API**
### User Authentication
 **Django Authentication**

## Main Features
This project supports **three types of users**, each with different functions and permissions.
### Player
Regular users, such as students and staff, earn points for completing environmental tasks.  
 **User system**: After registering and logging in, player can participate in game tasks.  
 **Task system**: Player can complete recycling challenges, campus walks challenges and environmental knowledge competitions.  
 **Location check-in**: Player can check in using QR code or GPS to verify task completion.  
 **Point reward**: Player can earn points after completing missions, which can be used for leaderboard ranking.  
 **Leaderboards**: Player can view their points ranking, which can inspire more people to participate in environmental action.  
 **Data security**: User information complies with GDPR regulations to ensure privacy and security.
### Game Keeper
Game keeper is responsible for creating and managing applications, managing tasks and auditing user data, which can be students or staff.  
 **Task management**: Game keeper can add, modify, delete tasks, and adjust the game rules.  
 **User audit**: Game keeper can view user check-in records, GPS records, and audit task completion.  
 **Data analysis**: Game keeper can view points statistics, leaderboards and other data to optimize the game experience.  
 **Security management**: Game keeper monitors unusual behavior.  
### Developer
Developer is responsible for building, extending and redeploying applications, which can be team development members or future technical support staff.  
 **Code maintenance**: Developer can access the GitHub code base, modify and optimize the code.  
 **Feature extensions**: Developer can develop new quests, new verification methods, new leaderboard rules, etc.  
 **API design**: Developer can maintain the Django REST API to ensure smooth data interaction.  
 **Database management**: Developer can optimize SQLite data structures to improve storage efficiency.  
 **Security update**: Developer can fix vulnerabilities and optimize user authentication.  

## Task Description
### Game task1: Campus Recycling
 **Goal**: Guide users to get used to garbage classification and improve recycling awareness.  
 **Interactive method**: Users recycle at least 5 plastic bottles on campus and go to the designated recycling site on campus to scan the QR code for check-in. The back-end system checks the user sign-in data to confirm whether the task is completed.  
 **Setting**: Users can complete this task once per day at each specified station. The user can get 10 points after completing the task.  
### Game task2: Green Travel
 **Goal**: Encourage users to reduce carbon emissions and raise awareness of sustainable mobility.  
 **Interactive method**: The user uses GPS positioning to record the walking data. When the user's walking data reaches 3 kilometers, the system automatically confirms the completion.  
 **Setting**: The user can get 30 points after completing the task.  
### Game task3: Sustainability Quiz
 **Goal**: Through interactive Q&A, let users learn environmental protection knowledge.  
 **Interactive method**: After the user clicks "Start Quiz" button, the system randomly selects 5 single choice questions related to environmental protection. After the user completes the quiz, the system scores and gives feedback.  
 **Setting**: Each quiz has 5 questions and each question is worth 5 points. After the user answers each question, the system will give feedback in time.  

## Leaderboard System
The leaderboard is ranked by points, and is used to motivate users to take more environmental action.
 **Ranking rule**: Those with higher points rank higher. 
 **Example**  
 **Rank | Avatar | Username | Points**  
   ------------------------------------------  
    1   |   A    |   A     |  30  
    2   |   B    |   B     |  20  
    3   |   C    |   C     |  10  

## Project Structure
GreenQuest/  
│── GreenQuest/  
│   │── __pycache__/  
│   │── __init__.py  
│   │── asgi.py  
│   │── dashboard_setting_test.py  
│   │── settings.py  
│   │── urls.py  
│   │── wsgi.py  
│── Specification/  
│── core/  
│   │── __pycache__/  
│   │── migrations/  
│   │── static/  
│   │   │── pictures/  
│   │   │── navpage2.css  
│   │   │── navpage2.js  
│   │   │── navpage2_test.py  
│   │   │── profile.css  
│   │   │── profile.js  
│   │   │── questions.css  
│   │   │── questions.js  
│   │   │── quiz.css  
│   │   │── quiz.js  
│   │   │── result.css  
│   │   │── result.js  
│   │   │── script.js  
│   │   │── script_test.py  
│   │   │── style.css  
│   │   │── walkinggame.css  
│   │   │── walkinggame.js  
│   │── templates/  
│   │   │── core/  
│   │   │   │── django_test_login.py  
│   │   │   │── django_test_signup.py  
│   │   │   │── login.html  
│   │   │   │── signup.html  
│   │   │   │── navpage2.html  
│   │   │   │── profile.html  
│   │   │   │── questions.html  
│   │   │   │── quiz.html  
│   │   │   │── result.html  
│   │   │   │── walkinggame.html  
│   │   │── registration/  
│   │   │   │── password_change_done.html  
│   │   │   │── password_change_form.html  
│   │   │   │── password_reset_email.html  
│   │── __init__.py  
│   │── admin.py  
│   │── apps.py  
│   │── auth_backends.py  
│   │── forms.py  
│   │── models.py  
│   │── tests.py  
│   │── urls.py  
│   │── views.py  
│── media/  
│   │── avatars/  
│   │── qr_codes/  
│   │── quiz_questions/  
│── db.sqlite3  
│── manage.py 
│── README.md    

## Live Demo
You can access the developed vision of this project at this following link: https://greenquest-ge4y.onrender.com

## Project operation
git clone https://github.com/amcaye/ECM2434.git  
cd ECM2434  
python -m venv venv  
venv\Scripts\activate  
pip install -r requirements.txt   
python manage.py migrate  
python manage.py runserver  
Then use the browser open http://127.0.0.1:8000/login/  

## Running tests
python manage.py test  
