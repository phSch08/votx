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
- Weblink on PDF
- QR Code on PDF
- Admin: generate PDF in VoteGroup card?
- Admin: generate PDF set strings in interface
- Multiple Votes in Frontend
- Random Value for vote in Frontend
- Deployment (done, noch prüfen)
- Handle Error: Registration Token already used
- Handle Error: Invalid Voter Token
- DB access data in env

Could Have:
- Multi Language Support
- equal name scheme
- Tests