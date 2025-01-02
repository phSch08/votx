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
fastapi dev votx/main.py
```

## TODOs

- logout from admin interface
- display vote results in admin interface?
- delete votes/votegroups
- dont allow changes as soon as ballot has been activated
- Websocket via TLS (wss://) sicherstellen
- Check that all incoming and outgoing data is piped through pydantic
- equal name scheme
- order vote options by option index
- disable dangerous functions in admin interface
- Configure PDF in webinterface
- Weblink on PDF
- QR Code on PDF
- Admin: Regisseur Card
- Admin: generate PDF in VoteGroup card?
- Admin: see results before publishing to beamer
- Admin: export of results
- Deployment
- Tests