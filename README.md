

## Setup on lxplus

```sh
lxplus$ git clone https://github.com/mazurov/thesis-code.git
lxplus$ cd thesis-code
lxplus$ mkdir data
lxplus$ cp ~amazurov/public/concezio/mc.db data/

lxplus$ nsls /castor/cern.ch/user/a/amazurov/data/ # list of datasets. You can set them in configs/tuples.json
lxplus$ xrdcp xroot://castorlhcb.cern.ch/castor/cern.ch/user/a/amazurov/data/chib2011_v4.root data/chib2011_v4.root

lxplus$ SetupProject Bender
lxplus$ ./fit.py -i --decay=chib1s --year=2011 --ptbegin=14 --ptend=18
lxplus$ ./fit.py -i --decay=ups --year=2011 --ptbegin=14 --ptend=18
```
