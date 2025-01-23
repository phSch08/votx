# VotX

[![Linter](https://github.com/phSch08/votx/actions/workflows/check_linting.yml/badge.svg)](https://github.com/phSch08/votx/actions/workflows/check_linting.yml)
[![Formatter](https://github.com/phSch08/votx/actions/workflows/check_formatting.yml/badge.svg)](https://github.com/phSch08/votx/actions/workflows/check_formatting.yml)

Written with Python Verions 3.12


Create .env file using the provided script:
```
python generate_env.py
```

Start Database
```
docker-compose up -d
```

Start Service
```
python run_votx.py
```

Linting/Formatting
```(bash)
$ ruff check [--fix | --watch]
$ ruff format
```

## TODOs

Must Have:


Should Have:

- Websocket via TLS (wss://) sicherstellen (done, noch prüfen)
- Check that all incoming and outgoing data is piped through pydantic
- QR Code on PDF
- Admin: generate PDF in VoteGroup card?
- Admin: generate PDF set strings in interface
- Deployment (done, noch prüfen)
- option to disable custom token in vote
- warning when trying to logout
- Beamer view with long strings looks bad
- PDF view with long answers looks bad


Could Have:
- Multi Language Support
- equal name scheme
- Tests
- possibility to not vote