# Kozo
Kozo is an commandline extention of the stock broker Robinhood. Taking advantage of Robinhood's API, Kozo extends various features that Robinhood is missing.
## Implemented Features
- Trailing Stoploss
- Time scheduled buys
## Features to Add
- A sustainable testing model with a mock API
- Trailing Stoploss to be independentally ran
- Add email notification
- Web UI
## Current issues
- The email notification for the scheduled buy is only printing to a local file (scheduled_buy.log).
- Timezone for the local machine must be set to PST
## Installation and use
This project, in its current state, is not setup for widespread use. If you do choose to run it either for curiousity, testing, or for monetary gain, know that it is far from being complete and needs more testing to be done (as well as refinement of features). Also, at the moment there is no user friendly way of installing and update the program. Thus, you will need some technical knowledge to run it. If you have any questions, please message me on [reddit](http://www.reddit.com/u/piratesearch).
### Requirements
All items listed are subject to change (most likely on a day to day basis)
- Python 2.7 (will work on developing it in 3.5 soon)
- Python packages:
  - requests
  - PrettyTable
  - python-crontab
  - getpass
- Ensure crontab is functional on the local machine
### Installation
At the moment, the only way to install Kozo is through downloading the source code and manually running `run.py`. If you do not know how to do this, the program is not ready for you to use. Sorry!
