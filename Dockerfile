FROM python:3.11

LABEL maintainer="Nikita Orlov <orlov.n@mamod.io>"

RUN apt-get update -y
RUN apt-get upgrade -y

RUN apt-get install -y wget

RUN apt-get -f install -y fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0  \
    libatspi2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libgtk-4-1 libnspr4 libnss3  \
    libu2f-udev libvulkan1 libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils libxtst6
RUN apt-get update && apt-get install -y npm

RUN pip install playwright
RUN pip install pytest-playwright playwright -U
RUN npm install -g npx
#RUN npm install -g playwright
RUN npx playwright install
RUN /bin/sh -c "playwright install"

RUN PLAYWRIGHT_BROWSERS_PATH=/app/ms-playwright python -m playwright install --with-deps chromium
RUN apt-get update && playwright install-deps

RUN apt install xvfb -y
RUN export DISPLAY=:1
RUN Xvfb $DISPLAY -screen $DISPLAY 1280x1024x16 &

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb

RUN mkdir /main_app

COPY . /main_app/

RUN pip install --no-cache-dir --upgrade -r /main_app/requirements.txt

WORKDIR /main_app

ENTRYPOINT ["python3", "runner.py"]
