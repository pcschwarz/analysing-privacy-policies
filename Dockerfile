FROM python:3-onbuild

RUN pip install -r requirements.txt

COPY ./ /usr/src/analysing-privacy-policies

EXPOSE 8051

CMD ["python", "app.py", "0.0.0.0", "8050"]
