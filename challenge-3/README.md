# Challenge-3
> Containerize the HTTP server implemented in server.py with docker. Please create the necessary Dockerfile. What result does making a GET request to the server with the header Challenge: orcrist.org return?


## how-to obtain the result
1. Build the container image: `docker build -t challenge-3-server challenge-3`
2. Start the container and expose port `8080`: `docker run --rm -p 8080:8080 challenge-3-server`
3. Send a GET request with the required header: `curl -i -H 'Challenge: orcrist.org' http://localhost:8080`                            


## executed commands
- `docker build -t challenge-3-server challenge-3`
- `docker run --rm -p 8080:8080 challenge-3-server`
- `curl -i -H 'Challenge: orcrist.org' http://localhost:8080`

**Example for a passing test** 
terminal> `curl -i -H 'Challenge: orcrist.org' http://localhost:8080`

```
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.14.5
Date: Tue, 19 May 2026 17:55:02 GMT
Content-type: text/html

Everything works!%
```

**Example for a failing test**
terminal> `curl -i -H 'Challenge: google.com' http://localhost:8080`

```
curl -i -H 'Challenge: google.com' http://localhost:8080
HTTP/1.0 404 Not Found
Server: SimpleHTTP/0.6 Python/3.14.5
Date: Tue, 19 May 2026 17:59:12 GMT
Content-type: text/html

Wrong header!%
```

**Example Output of the Docker log**
```
192.168.65.1 - - [19/May/2026 17:55:02] "GET / HTTP/1.1" 200 -
INFO:root:Host: localhost:8080
User-Agent: curl/8.7.1
Accept: */*
Challenge: orcrist.org

192.168.65.1 - - [19/May/2026 17:58:48] "GET / HTTP/1.1" 404 -
INFO:root:Host: localhost:8080
User-Agent: curl/8.7.1
Accept: */*
Challenge: google.com
```



## short explanation
- **Optimize**: select the most suiting :tag and pull the image version into a private registry
- The Python server only depends on the Python standard library, so the Dockerfile can stay very small.
- The selected base image is `dhi.io/python:3.14-sfw-ent-dev`.
- I chose this because Orcrist is security-focused and the Docker Hardened Images Python line is designed for stronger supply-chain and compliance posture, including published security metadata and enterprise-focused hardened variants.
- I selected this tag because it keeps the image on the Python `3.14` minor line while still allowing patch-level updates, which is a better maintenance tradeoff than pinning to a full patch version such as `3.14.5`.
- I kept the Dockerfile intentionally simple to reduce operational effort: copy the script, expose `8080`, and start `python server.py`.
- The hardened image family is also attractive for long-term support and compliance-oriented environments because it is positioned with extended lifecycle support and CIS/FIPS/STIG-oriented security posture.
- A GET request with header `Challenge: orcrist.org` returns: `Everything works!`

## Also useful to know
Check for SVEs of the docker image `docker scout cves local://challenge-3-server:latest`

**Example**
                   │                    Analyzed Image                     
───────────────────┼───────────────────────────────────────────────────────
 Target            │  local://challenge-3-server:latest                    
   digest          │  088abde91615                                         
   platform        │ linux/arm64                                           
   provenance      │ https://github.com/chriscloud27/orcrist-challenge.git 
                   │  73c89ad18e4d578a90b61e32999c4c8df3a75261             
   vulnerabilities │    0C     0H     3M    21L                            
   size            │ 74 MB                                                 
   packages        │ 105      

// layers and reports here

24 vulnerabilities found in 10 packages
  CRITICAL  0  
  HIGH      0  
  MEDIUM    3  
  LOW       21 
