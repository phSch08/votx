from dotenv import load_dotenv
from votx.main import app
import uvicorn
import os

if __name__ == "__main__":
    load_dotenv('.env')
    load_dotenv('db.env')
    
    print(os.environ.get('DB_HOST'))
    uvicorn.run("votx.main:app", reload=True, host="127.0.0.1", port=8000)