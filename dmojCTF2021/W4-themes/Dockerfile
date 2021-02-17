from debian:buster
EXPOSE 5004/tcp

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates

RUN update-ca-certificates

WORKDIR /code
copy * /code/

RUN chmod +x /code/server

CMD ["./server"]