# Overview
A simple to use Python script for connecting to the TradeStation server.
Currenty this scripted only has the function for connecting to and refreshing the connection with the Tradestation server. However I believe it acomplishes this task more simply and robustly than previous work. 

# Getting Started
* First download this repository. The folder contains all that is required. However it will import some common libraries that are easy to install if they are not available. I recommend using Visual Studio Code for working with the library. If they are not installed VS code will mark them as not found when opening the scripts in the “ts” folder. 
* Second, enter id key and secret key into secret/credentials.json These were provided by TradeStation, likely in an email with a password protected PDF. 
* Last, run main.py in the library root. This is an example script which shows how to use the library. Note that when connecting to the TradeStation servers for the first time, you will need to manually login to TradeStation through a web server, which will then send an authorization code to the script through the URL (saved in secret/ts_state.json). I worked hard to make as much of this process as automatic and self explanatory as possible. 

# Return the Favor
I spent my precious free hours as a new dad making this script usable for others. I did this in an effort to give back to the world of people who have made my life better with all the hours they dedicated to free software I use. 

The purpose of this script is to help make you money. If it helps add benefit to your life please pay it forward by either helping me add features to this library or find other ways to make life better for others. 

# Credits
Project uses code from both pattertj/ts-api and also Himangshu4Das/tradestation-v3-python-api. It appears both projects are stale and after spending a lot of time with both I decided to start a new project for the freedom to carry their work further. While I believe this project will offer some valuable improvements above the previous work, please know that both of these projects were both used as a starting point. 