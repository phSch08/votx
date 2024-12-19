# Votick

Written with Python Verions 3.12

Start Database
```
docker-compose up -d
```

Start Service
```
fastapi dev main.py
```

## TODOs

- JWT Token expiry testen
- auto JWT Token expiry renewal
- fully functional admin interface
- redirect to login when unauthenticated
- admin password changeable
- logout from admin interface
- beamer display
- display vote results in admin interface?
- delete votes/votegroups
- dont allow changes as soon as ballot has been activated
- Websocket via TLS (wss://) sicherstellen
- Check that all incoming and outgoing data is piped through pydantic
- equal name scheme
- order vote options by option index