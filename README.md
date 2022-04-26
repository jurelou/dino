<p align="center"><img width="100" src="https://user-images.githubusercontent.com/30180021/165300879-192aee12-2cba-4125-9137-af6450daa2d0.png" alt="Vue logo"></p>
<h2 align="center">DINO</h2>

<div align="center">
 <p>
  <strong>
   New generation forensics ETL
  </strong>
 </p>
 <p>
  <img width="85" src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336">
  <img width="100" src="https://img.shields.io/badge/code%20style-black-000000.svg">
  <img width="95" src="https://img.shields.io/badge/security-bandit-yellow.svg">
  <img width="75" src="https://img.shields.io/badge/python-3.8-blue">
 </p>
</div>

# Requirements

- [docker-compose v2.X](https://github.com/docker/compose/releases/tag/v2.4.1)

# Installation

Clone the repository (including sub modules) with:
```
git clone --recurse-submodules https://github.com/jurelou/dino
cd dino
```

If necessary, modify `ROOT_FOLDER` in the `.env` file. This is the folder containing your artifacts to analyze.
Then, run:
```
make
```

Wait a few moments, then you should have:
- a splunk instance running on port `8000`
- dagit GUI on port `3000`

You can start launching jobs via dagit!

# Root folder layout:

```
/DINO_ROOT/
├── DINO_SPLUNK_UNIVERSAL_FORWARDER/
│   ├── autoruns/
│   ├── evtx/
│   ├── ntfs/
│   ├── ntfs-i30/
│   ├── ntfs-pehash/
│   ├── ntfs-secdescr/
│   ├── usn/
│   └── zircolite/
├── __DINO_TEMP/
└── ...

```
# Supported DFIR-ORC artifacts

|Artifact name | parsing | splunk `source` |
|--|--|--|
|evtx | :heavy_check_mark: | evtx |
|evtx - sigma rules | :heavy_check_mark: | zircolite |
|Autoruns | :heavy_check_mark: | autoruns |
|ntfs | :heavy_check_mark: | ntfs |
|ntfs $i30 | :heavy_check_mark: | ntfs_i30 |
|ntfs pehash | :heavy_check_mark: | ntfs_pehash |
|ntfs secdescr | :heavy_check_mark: | ntfs_secdescr|
|usn | :heavy_check_mark: | usn |
|mft | :heavy_check_mark: | mft |
|SAM hives | :heavy_check_mark: | sam_hives |
|User hives | :heavy_check_mark: | user_hives |
|System hives | :heavy_check_mark: | system_hives |
|RAM | :x: | :x:|
|TextLogs | :x: | :x:|
|tcpvcon | :heavy_check_mark: | tcpvcon |
|PsService | :heavy_check_mark: | psservice |
|tcpvcon | :x: | :x:|
|Listdlls | :x: | :x:|
|GetSamples* | :x: | :x:|
|AuditTool | :x: | :x:|
|CatRoot | :x: | :x:|
|Browsers history | :x: | :x:|
|bootcode | :x: | :x:|
|Artefacts | :x: | :x:|
|ARKUser | :x: | :x:|
|ADS | :x: | :x:|
|files - yara rules | :x: | :x:|

# Known bugs

- CRC32 errors while trying to unzip ORCs
- When converting csv to json, some keys have quotes, (eg. "ComputerName")
- 
# TODO

- csv files: remove empty values
- splunk HEC optimization (bulk insert)
- set correct host values
- make a clean dev environment whithout having to rebuild everything
- maybe use a threadpool in the evtx parser (until dagster allow us to use nested DynamicOut)
- allow to skip/disable artifacts
- registry parser raises a lot of errors, a lot of keys might not be parsed


## Built With

* [Dagster](https://dagster.io/) - The data orchestration platform
* [evtx](https://github.com/omerbenamram/evtx) - Fast (and safe) parser for the windows event logs
* [Zircolite](https://github.com/wagga40/Zircolite) - Standalone SIGMA-based detection tool for EVTX
