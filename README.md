# Master Server

## Archival notice

I'll be archiving this repository, and sun-setting the testing server (`master.quake.services`), as I no longer have the time to maintain it or implement the changes needed to see it fully realised.

The testing server will be decommed sometime within the next couple of months, depending on current usage and whether any migration steps need to be taken.

Thank you to all who helped out along the way :-)

## Description 
This project aims to replicate the functionality of the idSoftware master server (satan.idsoftware.com) in Python.

Currently the server is available for testing purposes on `master.quake.services`. For more information on usage [here](https://docs.quake.services/usage/servers/).

## Project Goals

Core goals:
-  Respond to queries from server browsers such as qstat
-  Respond to queries and updates from Quake 2 servers
-  Support for protocol 35, 36 (Q2Pro), and 37 (R1Q2)
-  Be extensible enough to support other idTech engines/games

Stretch goals:
-  Support all common Quake, Quake 2, and Quake 3 derived servers and clients
-  Aggregation of existing master server lists
-  Support IPv6 servers and clients

Documentation and additional information can be found here: [Documentation](https://docs.quake.services/)
