# web-frontend

Static site to communicate with [web-backend](https://github.com/quakeservices/web-backend)

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
