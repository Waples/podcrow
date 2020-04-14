# podcrow

_Download your podcasts and maintain history via your terminal (where you are and where you should stay)._

### Notice
honorable mention to `podfox` for the inspiration.

### Usage:
I still need to package this, but in the meantime, just run `python podcrow <OPTS>`.

```
usage: podcrow.py [-h] [-a AMOUNT] [-i IMPORT_POD_FEED] [-l] [-s SHORT]
                  [-d DOWNLOAD] [-u] [-p] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -a AMOUNT, --amount AMOUNT
                        amount of pods to download.
  -i IMPORT_POD_FEED, --import-pod-feed IMPORT_POD_FEED
                        import_pod feed with rss-url.
  -l, --list            list available feeds.
  -s SHORT, --short SHORT
                        defines a short for the pod.
  -d DOWNLOAD, --download DOWNLOAD
                        download all undownloaded items.
  -u, --update          update feeds.
  -p, --update-podcrow  update podcrow binary.
  -v, --version         Show the version.
```
