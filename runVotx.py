from dotenv import load_dotenv
from votx.main import app
import uvicorn

if __name__ == "__main__":
    load_dotenv('.env')
    load_dotenv('db.env')
    uvicorn.run("votx.main:app", reload=True, host="127.0.0.1", port=8000)