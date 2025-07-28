A simple python script to synchronize [Mopidy](https://mopidy.com) and [Shairport-Sync](https://github.com/mikebrady/shairport-sync) media players. This script will monitor each player 
activity and once a player starts playing it will stop the other player.

You should use it as a daemon for example : 

```
shairmopd &
```

Or the following `systemd` service file :

```
[Unit]
After=shairport-sync.service
After=mopidy.service

[Service]
ExecStart=/usr/bin/shairmopd

[Install]
WantedBy=multi-user.target
```
