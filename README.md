# Charlie Pi 🐈‍⬛🥧

### Install
With [pipenv][pipenv]:
```
pipenv install --site-packages
```

### Run
The following command will install and run all processes as systemd daemons:
```
pipenv run main
```
You can also run individual services as normal foreground processes, for example:
```
pipenv run web_app
pipenv run sht30_recorder
```
If a process is running as a daemon, make sure you disable it before attempting to run it as a foreground process.

[pipenv]: https://github.com/pypa/pipenv
