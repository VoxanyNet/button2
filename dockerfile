FROM python:3.10.13-bookworm

WORKDIR /usr/src/app

# make module folder
RUN mkdir button

RUN pip install py-cord

# copy contents of the module to the module folder in container
COPY ./button ./button


CMD ["python", "-m", "button"]
