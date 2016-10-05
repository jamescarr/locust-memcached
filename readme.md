# MemcachedLocust
Uses locust to do distributed load testing against memcached.


## Running it Locally
`docker-compose up -d` is ran only the target and the locust master will
come up, the slave will die right away (because by the time it tries to
come up, master is not available).

If we wanted to run 4 locust minions to distribute tasks amongst we'd
run `docker-compose scale minion=4` to launch 4 containers. If we log
into the locust interface at http://dockerhost:8089 we should see 4
slaves connected.

