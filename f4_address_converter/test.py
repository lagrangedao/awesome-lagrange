import base64

def add_base32_padding(encoded_text):
    padding_needed = 8 - (len(encoded_text) % 8)
    return encoded_text + '=' * padding_needed

def remove_f4_prefix(encoded_text):
    prefix = "f410f"
    if encoded_text.startswith(prefix):
        return encoded_text[len(prefix):]
    else:
        return None


def convert_address_f4_0X(encoded_text):

    if encoded_text is not None and len(encoded_text) == 44:
        encoded_text = remove_f4_prefix(encoded_text)
        encoded_text_with_padding = add_base32_padding(encoded_text.upper())
        decoded_bytes = base64.b32decode(encoded_text_with_padding)

        # Discard the last 4 bytes
        decoded_bytes = decoded_bytes[:-4]

        hex_string = "0x"+decoded_bytes.hex()
        print(hex_string)
        return hex_string
    else:
        print("Incorrect f4 address format")

#Example operation
convert_address_f4_0X("f410feg3ft4kw2jurlbe6kyd7ijron66ocjhjebvwrfi")