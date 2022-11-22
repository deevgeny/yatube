# Social network of bloggers

Yatube - social network of bloggers. Here you can register, publish posts, 
add pictures to them, leave comments on posts and subscribe to your favorite 
authors.


## Technology stack
 - Python 3.7
 - Django 2.2.16


 ## ORM - models
- Post - authors posts.
- Group - authors communities.
- Comment - posts comments.
- Follow - subscriptions.

 ## Web application
Yatube consists of several applications, each of which is responsible for
a specific functional part of the project.
- users - user registration and authentication.
- posts - authors posts, comments and subscriptions.
- core - paginator and custom error pages.
- about -  information about projects.

## How to install and run
```
# Clone the repository
git clone https://github.com/evgeny81d/yatube

# Go to the project directory
cd yatube

# Create Python 3.7 virtual environment
python3.7 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt --upgrade pip

# Run migrations
python3 yatube/manage.py migrate

# Create superuser
python3 yatube/manage.py createsuperuser

# Run project on django development server
python3 yatube/manage.py runserver
```

## Finally web application is ready for use

 [http://127.0.0.1:8000/](http://127.0.0.1:8000/) - home page
 
 [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) - admin site

