# Kozo
Kozo is an commandline extention of the stock broker Robinhood. Taking advantage of Robinhood's API, Kozo extends various features that Robinhood is missing.
## Implemented Features
- Trailing Stoploss
- Time scheduled buys
## Features to Add
- Trailing Stoploss to be independentally ran
- Add email notification
- Web UI
## Current issues
- The path location for the scheduled buy is hardcoded and will not work
on other user's machines. This is done for development currently and will
be fixed soon
- The email notification for the scheduled buy is only printing to a local file.
- Timezone for the local machine must be set to PST
