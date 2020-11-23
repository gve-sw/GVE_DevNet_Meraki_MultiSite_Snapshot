Meraki Multi-Site Snapshot
-------------------------------------

A Prototype built to leverage Meraki network technology and Meraki Snapshot API to take Multi-Site snapshots at any given point in time.


## Contacts
* Alexander Hoecht

## Solution Components
* Python 3 [Download latest version](https://www.python.org/downloads/)
* Flask
* HTML / CSS / JQuery

## Installation/Configuration
Steps needed to install and configure the project's environment
```
1) Clone GitHub Repo
    * git clone <repoURL>
2) From Repository, Create Virtual Environment
    * python3 -m venv venv
    * source venv/bin/activate
3) Install Dependancies
    * pip install -r requirements.txt
4) Set up Flask Environment
    * export FLASK_APP=src
    * export FLASK_ENV=development
```

## Usage
Steps needed to start the project (<b>Must Complete Installation/Configuration Steps FIRST!</b>)
```
1) Initialize Project DB
    * flask init-db
2) Initialize Application
    * flask run
3) Navigate to URL
    * http://127.0.0.1:5000/ (by default)
```

# High-Level Diagram

![/IMAGES/HLD_Multisite_Snap.png](IMAGES/HLD_Multisite_Snap.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.