# influx-neptunapex
Feed data from a neptune apex into influxdb

Simple setup:

* install an influxdb
* create a database named "apex":
  influx
  create database apex
* run the influx feeder:
  influx-neptuneapex --host :my-apex-ip or hostname:
