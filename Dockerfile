FROM golang:alpine3.14
MAINTAINER Nate River 'n1ra@red-eye.works'
RUN mkdir /app 
ADD src/ /app/ 
WORKDIR /app
ENV GO111MODULE=off
RUN apk update && apk add git && go get golang.org/x/net/proxy && go build -o main .
CMD ["/app/main"]
EXPOSE 8080