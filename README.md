# MoviesDiary

#### Description:

- ##### MoviesDiary is a simple website for browsing movies and tv shows information.   

- ##### The application allows user to create a profile where they could add movies to either their watchlist or favourtites list.

- ##### Users would be recommended movies based on movies on their favourites list.

#### Stack 

- ##### The application was developed using flask framework.

- ##### On the frontend i used html, css and bootstrap.

- ##### Also used the imdb api for providing data about the movies.

#### Project Structure

- ##### The application was designed using the mvc design pattern.

1. ##### Model/Database

- ##### The application is developed using sqlite3.

- ##### I used sqlalchemy orm for controlling and modifying the database.

2. ##### Templates

  ##### Inside of the templates file we have our views which contains:

 - ##### Index.html which points to the home page

 - ##### mostpopular.html which points to the top 250 movies page

 - ##### search.html which points to the search results page

 - ##### title.html which points to a certain movie

 - ##### person.html which points to a certain person

 - ##### watchlist.html which points to the user's watch list

 - ##### favlist.html which points to the user's favourites list

 - ##### profile.html which points to the user's profile page

 - ##### register.html which points to the registration page where users could create an acount

 - ##### login.html which points to the login page where users could login to their account

 3. #### Controller

  - ##### Inside of app.py is the logic of the application where i fetch data from the imdb api and send it to the templates.

  - #### Also the database is handled in app.py via sqlalchemy
