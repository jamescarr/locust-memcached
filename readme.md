# MemcachedLocust
Uses locust to do distributed load testing against memcached.


## Running it Locally
1. Run `docker-compose up -d`
2. Navigate to http://dockerhost:8089
3. Run!

You can also scale up the number of minions by running `docker-compose
scale minion=4`


## Details
* Set `min_set_size` and `max_set_size` to set the boundries for random
  cache value sizes

* Set `number_of_keys` to create a defined pool of keys to set/get


