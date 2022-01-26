<<<<<<< HEAD
# Overview

This project as an attempt to replicate the idSoftware master server for Quake 2 (satan.idsoftware.com) in Python 3.

Core goals:
-  Respond to queries from server browsers such as qstat
-  Respond to queries and updates from Quake 2 servers
-  Support for protocol 35, 36 (Q2Pro), and 37 (R1Q2)
-  Be extensible enough to support other idTech engines/games

Stretch goals:
-  Support all common Quake, Quake 2, and Quake 3 derived servers and clients
-  Aggregation of existing master server lists
-  Multiregion support
-  Support IPv6 end-to-end where applicable

Documentation and additional information can be found here: [Documentation](https://github.com/quakeservices/documentation/)

## web-frontend

Static site to communicate with web-backend

TODO:

| Path | Description | MVP |
| ---- | ----------- | --- |
| `/` | redirect to /servers | yes |
| `/servers` | Contains list of all servers | yes |
| `/servers/<game>` | Contains a list of all servers for a specific game | no |
| `/how-to` | Information for server/software maintainers, and users on using these services | yes |
| `/news` | Changelog, possibly related blog | no |
| `/about` | Information about the project, "why" and such | no |
| `/contact` | Methods of contact | no |

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
