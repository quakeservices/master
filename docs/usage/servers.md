# Servers

## Quake 2

Setting the master of a running Quake 2 server:

```
setmaster master.quake.services
```

Example output from the above command:

```console
setmaster 127.0.0.1
Master server at [127.0.0.1]:27900
Sending a ping.
Ping acknowledge from [127.0.0.1]:27900
Sending heartbeat to [192.246.40.37]:27900
Sending heartbeat to [127.0.0.1]:27900
Ping acknowledge from [127.0.0.1]:27900
```

Quake 2 will send a ping a ping, and once it receives an acknowledgement, will send a heartbeat.

It's recommended that this be set as part of your server config for simplicity along with any other master servers you're using.
