# Servers

## Quake 2

Setting the master of a running Quake 2 server:

```
setmaster master.quake.services
```

Example output from the above command:

```console
setmaster 52.39.209.179
Master server at [52.39.209.179]:27900
Sending a ping.
Ping acknowledge from [52.39.209.179]:27900
Sending heartbeat to [192.246.40.37]:27900
Sending heartbeat to [52.39.209.179]:27900
Ping acknowledge from [52.39.209.179]:27900
```

Quake 2 will send a ping, and once it receives an acknowledgement, will send a heartbeat.

It's recommended that this be set as part of your server config for simplicity along with any other master servers you're using.

<!-- prettier-ignore-start -->
!!! warning

    Always use the hostname `master.quake.services` and not any of the addresses that it resolves to.
    The reason for this is that due to the nature of the AWS Load Balancer service those IP addresses may change without notice.
<!-- prettier-ignore-end -->

## FAQ

**Q**: Why is my server also sending a ping to `192.246.40.37`?

**A**: Because `192.246.40.37` is the original master server run by id Software that no longer exists.
[Source](https://github.com/id-Software/Quake-2/blob/372afde46e7defc9dd2d719a1732b8ace1fa096e/server/sv_init.c#L360-L363)
