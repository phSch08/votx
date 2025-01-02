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

- dont allow changes as soon as ballot has been activated
- Websocket via TLS (wss://) sicherstellen
- Check that all incoming and outgoing data is piped through pydantic
- equal name scheme
- order vote options by option index
- disable dangerous functions in admin interface
- Weblink on PDF
- QR Code on PDF
- Beamer: url below logo
- Admin: Regisseur Card
- Admin: generate PDF in VoteGroup card?
- Admin: generate PDF set strings in interface
- Admin: see results before publishing to beamer
- Admin: display custom message
- Admin: display VotX logo if no message configured
- Admin: export of results
- Multiple Votes in Frontend
- Deployment
- Tests