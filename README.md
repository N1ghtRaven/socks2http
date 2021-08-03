Socks2Http
==========
### Build

````bash
$ docker build -t socks2http .
````

### Run

Using this docker-compose file as an example:

```yml
version: '3'
services:
    app:
        image: socks2http
        container_name: socks2http
        restart: unless-stopped
        ports:
            - 40001:40001
        environment:
            - SOCKS_HOST=127.0.0.1
            - SOCKS_PORT=1080
            - SOCKS_USERNAME=user
            - SOCKS_PASSWORD=password
```

