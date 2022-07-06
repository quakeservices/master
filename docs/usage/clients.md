# Clients

Clients in this case are end users querying the master server for the server list.

## Qstat

[qstat](https://github.com/multiplay/qstat) (aka quakestat) is currently the only client server browser with which this application has been tested.
However any other client that allows the user to specify a master server should work.

The following command will request the list of servers:

```
quakestat -q2m master.quake.services
```

Example output:

```
$ quakestat -q2m master.quake.services
ADDRESS           PLAYERS      MAP   RESPONSE TIME    NAME
Q2M master.quake.services 1 servers    395 / 0
Q2S  116.240.207.35:27910   0/8   0/0     q2dm7     14 / 0            quake.services
```
