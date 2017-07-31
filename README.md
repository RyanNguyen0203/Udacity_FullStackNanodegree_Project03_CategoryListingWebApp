# Udacity Full Stack Nanodegree Program Project 3 - Log Analysis with Python and PostgreSQL
Build a ready-to-deploy CRUD web application with __Flask__ and __PostgreSQL__ allowing users to plan out the items they will need to buy for their new house.
Users' information and data integrity are protected with the implementation of Google's __AOuth 2.0__ for user's registration and sign-in as well as the use of __SQLAlchemy__ library for secure database query.
## Getting Started
1. Follow this [guide](https://goo.gl/Nx5u8L) to install VirtualBox and configure it with Vagrant
2. Open a virtual machine shell session by `cd` into the `/vagrant` subdirectory and typing these into your command shell:
`vagrant up`
`vagrant ssh`
3. The `/vagrant` directory is shared between the virtual machine and your computer (the system on which the virtual machine is running). Its default __absolute path__ inside the virtual machine is `/vagrant`. Type `cd /vagrant` to locate into this directory.
4. Clone this repository here and `cd` into the git folder
5. Set up the database by typing this into your terminal:
`python3 database-setup.py`
or
`python database-setup.py` ( _if your default Python version is 3_ )
6. Open `first_user_info.json` and enter the Gmail address that you will use to sign in to the app later. Doing this will give you access to the test data as its owner. If you want to start from clean slate and add your own data, skip this step as well as step 7 and resume from step 8.
7. Populate the database
`python3 populate-db.py`
or
`python populate-db.py`
8. Run the application from the virtual machine
`python3 main.py`
or
`python main.py`
9. Open your browser and type in
`http://localhost:5000/`
10. Sign in as a new user with the Gmail address from step 6 (or any other Gmail address if you skip this step) and start experiencing the app!

    **Note:**
    - This application is designed to run on `localhost:5000` so make sure your `port 5000` is available. If you are on Linux, try using `sudo netstat -nltp` to see which port is being used by which applications and then kill the one using `port 5000` with `kill -9 [application's PID]`
    - Don't try to change the port number in `main.py` as it will break the code
    - You can use your favorite text editor to play around with the code outside the virtual machine, as long as all the scripts is kept within `\vagrant`.

## Usage
All Python code is written in Python 3
