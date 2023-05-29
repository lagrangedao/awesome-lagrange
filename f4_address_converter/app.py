import base64

import uvicorn

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


def add_base32_padding(encoded_text):
    padding_needed = 8 - (len(encoded_text) % 8)
    return encoded_text + '=' * padding_needed


def remove_f4_prefix(encoded_text):
    prefix = "f410f"
    if encoded_text.startswith(prefix):
        return encoded_text[len(prefix):]
    else:
        return None


@app.get("/", response_class=FileResponse)
def read_root():
    return "./static/index.html"


@app.get("/convert_address_f4_0X")
def convert_address_f4_0X(f4Address: str):
    print(f4Address)
    if f4Address is not None and len(f4Address) == 44:
        encoded_text = remove_f4_prefix(f4Address)
        encoded_text_with_padding = add_base32_padding(encoded_text.upper())
        decoded_bytes = base64.b32decode(encoded_text_with_padding)

        # Discard the last 4 bytes
        decoded_bytes = decoded_bytes[:-4]

        hex_string = "0x" + decoded_bytes.hex()

        return {"fevm_address": hex_string}
    else:
        return {"error": "Incorrect f4 address format"}



app.mount("/", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
