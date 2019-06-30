FROM python:3.7-alpine

ARG APP_ROOT=/opt/geolocation-echo

RUN mkdir ${APP_ROOT}

ADD requirements.txt ${APP_ROOT}
ADD app.py ${APP_ROOT}
RUN pip install -r "${APP_ROOT}/requirements.txt"

RUN addgroup -S echo --gid 101 && adduser -S -G echo echo
RUN chown -R echo:echo ${APP_ROOT}
USER echo

WORKDIR ${APP_ROOT}

EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["./app.py"]