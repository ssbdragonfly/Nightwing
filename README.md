## Nightwing
A project to help keep your employees focused during long zoom and real life meetings with interactive quizzes!

Devolped by Shaurya Bisht, Aarush Deshpande, and Jacob Percy for the 10th District of Virginia's Congressional App Challenge.

### Demo (Click!)

[![Watch the video](https://img.youtube.com/vi/MAMqRrMCMKk/0.jpg)](https://www.youtube.com/watch?v=MAMqRrMCMKk)

### Features
- Real-time interactive quizzes during meetings
- Multi-choice questions with instant feedback
- Desktop client for quiz participants
- Web interface for quiz creators
- Credit system for engagement
- Easy-to-use interface for creating and managing quizzes

### Components
- Django web application for quiz management
- Custom desktop client built with CustomTkinter
- Store system for credit management

#### Developing
Clone the repo, and install dependencies
```
git clone https://ssbdragonly/CAC24 nightwing
cd nightwing
pip install uv
uv sync
```
Then migrate changes and run the server
```
python manage.py migrate
python manage.py runserver
```
