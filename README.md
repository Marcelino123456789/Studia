# Studia

#### Video Demo: <[Studia](https://youtu.be/hSzYX-qkVPM)>

#### Description:

Studia is my CS50 Final Project, a web-based student dashboard designed to help students organize different parts of their academic life in one place. The idea behind Studia came from the fact that students often use several separate applications to manage notes, tasks, time, schedules, and communication. Studia brings these functions together into a single platform with a simple and student-focused interface.

When a user first opens Studia, they can either register a new account or log in to an existing one. During registration, the application checks that a username, password, and password confirmation have been provided and that the two passwords match. The password is then hashed using Werkzeug's password hashing functions before it is stored in the database. Passwords are therefore not stored as plain text. After successful registration or login, the user's ID is stored in a Flask session, which allows the application to identify the currently logged-in user.

The first main feature is **Notes**. Users can create personal notes by providing a title and content. Notes are stored in the SQLite database and are associated with the user who created them. Users can also delete their own notes. When the Notes page is opened, the application retrieves the notes belonging to the current user and displays them.

The next feature is the **Timer**. Studia provides a persistent timer that allows users to enter a duration and start, pause, or stop the timer. Unlike a timer that exists only in the browser, Studia stores the timer's state in the database. The timer can therefore maintain information such as whether it is running or paused and how much time remains. The application uses JavaScript requests to communicate with Flask routes such as `/timer/start`, `/timer/pause`, `/timer/stop`, and `/timer/status`. The server uses the current time and the stored end time to calculate the remaining duration.

The third feature is **Tasks**. Users can create tasks and assign due dates to them. Tasks are stored together with the ID of the user who created them. The Tasks page retrieves only the current user's tasks and orders them by their due date. When a task is completed, the user can remove it from the database.

Studia also includes a **Calendar**. The Calendar retrieves the due dates of the current user's tasks and passes them to the calendar template. This provides a visual way for students to see when their tasks are due and helps them understand their schedule more easily.

Another part of Studia is the **Search and Chat system**. Users can search for another registered user by username. When a valid username is found, the application can save that user in the current user's friends list and open a conversation with them. The friends table uses a unique constraint on the user and friend name combination so that the same friend cannot be added repeatedly.

The **Chat** feature allows users to send messages to other registered users. Every message contains a sender ID, receiver ID, message content, a timestamp, and a read status. Conversations are retrieved from the database using both participants' IDs and are displayed in the correct conversation. Studia also tracks unread messages. When a user opens a conversation, messages received from that user are marked as read, while the Search page can display the number of unread messages from different users.

The main backend file is **`app.py`**. It contains the Flask application and the routes responsible for registration, login, logout, the dashboard, Notes, Tasks, Calendar, Timer, Search, Friends, and Chat. It also contains the database queries and the logic connecting the frontend with the SQLite database. Flask sessions are configured to store the current login state, and the application prevents cached responses so that pages containing user-specific information are not unnecessarily stored by the browser.

The **`helpers.py`** file contains helper functions used by the application, including the authentication-related `login_required` function and the `apology` function. These helpers make it possible to protect routes that should only be accessible to logged-in users and to display errors when an operation cannot be completed.

The **`templates/`** directory contains the HTML/Jinja templates used to display the application's pages. These templates provide the interface for pages such as the dashboard, login, registration, Notes, Tasks, Timer, Calendar, Search, Friends, Chat, and About. The **`static/`** directory contains the CSS, JavaScript, images, and other static resources used to control the appearance and interactive behavior of the application.

Studia uses **`Studia.db`**, a SQLite database accessed through the CS50 SQL library. The database contains tables for users, notes, tasks, messages, friends, and timers. Relationships between users and their data are maintained using user IDs. This design allows each logged-in user to access their own notes, tasks, timer, and other information without mixing their data with another user's data.

One important design choice was storing the timer in the database rather than relying entirely on JavaScript. This made the timer persistent and allowed the server to remain the source of truth for its state. Another design choice was associating application data with the logged-in user's ID. This keeps user data separated and makes the different features work together through the same authentication system.

I built Studia using concepts from CS50, including Python, Flask, SQL, SQLite, HTML, CSS, JavaScript, sessions, authentication, and database operations. Building the project helped me understand how the different parts of a complete web application communicate with one another. Most importantly, I wanted Studia to be more than a programming exercise: I wanted it to be a practical platform that could help students manage their academic life in one place.

This is Studia, my CS50 Final Project.
