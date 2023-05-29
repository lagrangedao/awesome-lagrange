from fastapi import FastAPI

from datetime import datetime

now = datetime.now()  # current date and time

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World! %s" % now.strftime("%m/%d/%Y, %H:%M:%S")}
