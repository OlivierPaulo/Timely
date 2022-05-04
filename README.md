# Install

Go to `https://github.com/{group}/Timely` to see the project, manage issues,
setup you ssh public key, ...

Create a python3 virtualenv and activate it:

```bash
sudo apt-get install virtualenv python-pip python-dev
deactivate; virtualenv -ppython3 ~/venv ; source ~/venv/bin/activate
```

Clone the project and install it:

```bash
git clone git@github.com:{group}/Timely.git
cd Timely
pip install -r requirements.txt
make clean install test                # install and test
```
Functionnal test with a script:

```bash
cd
mkdir tmp
cd tmp
Timely-run
```

# Description

Script use to automate time tracking by getting Data from Jira API query.
Objective is to generate a CSV to then import it to Google Calendar