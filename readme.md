# Votick
Written with Python Verions 3.12


Create .env file using the provided script:
```
python generateEnv.py
```

Start Database
```
docker-compose up -d
```

Start Service
```
python runVotx.py
```

## TODOs

Must Have:
- cannot delete votegroup


Should Have:

- Websocket via TLS (wss://) sicherstellen (done, noch prüfen)
- Check that all incoming and outgoing data is piped through pydantic
- order vote options by option index
- QR Code on PDF
- Admin: generate PDF in VoteGroup card?
- Admin: generate PDF set strings in interface
- Deployment (done, noch prüfen)
- Handle Error: Registration Token already used
- Handle Error: Invalid Voter Token
- DB access data in env
- disable custom token in vote
- warning when trying to logout


Could Have:
- Multi Language Support
- equal name scheme
- Tests
- possibility to not vote