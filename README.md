Simple tool to plumb http proxy requests through a socks5 proxy.

NOTE: this is a little rough. Known issues:

* We use most of the default settings for `net/http.Client`, so things
  like following redirects on the server-side will happen, which is
  probably not The Right Thing.

Also, I just haven't tested this super carefully. Buyer beware; you get
what you pay for.

Building:

    go build

Usage:
    SOCKS_HOST=<socks-proxy-host> SOCKS_PORT=<socks-proxy-port> SOCKS_USERNAME=<socks-proxy-username> SOCKS_PASSWORD=<socks-proxy-password> socks2http


docker-compose.yml:
```yml
version: "3"
services:
    socks2http:
        build: .
        image: n1ghtraven/socks2http:golang
        ports:
            - 40001:8080
        environment:  
            - SOCKS_HOST=127.0.0.1
            - SOCKS_PORT=1080
            - SOCKS_USERNAME=user
            - SOCKS_PASSWORD=password  
```

# License

MIT
