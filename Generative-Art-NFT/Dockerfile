# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /usr/src/app
COPY . /app


# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -i https://test.pypi.org/simple/ lag-sdk==0.4.12

# Make port 9999 available to the world outside this container
EXPOSE 9999

# # Define environment variable
# ENV MUMBAI_RPC=https://rpc-mumbai.maticvigil.com
# ENV SPACE_UUID=eccbf673-4277-4f54-a71d-0286d5be8771

ENV COMMANDLINE_ARGS="--listen --port=9999 --enable-insecure-extension-access --api"

# Run the Python script when the container launches
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=9999"]