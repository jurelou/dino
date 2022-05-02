from dagster import Field, config_mapping


@config_mapping(
    config_schema={
        "celery_executor": {
            "broker": Field(str, description="Celery broker url", default_value='pyamqp://dino:SPKKJxqHIc1OS92raTeo@rabbitmq:5672/dino') 
        },
        "splunk": {
            "host": Field(str, description="Splunk hostname", default_value="splunk"),
            "port": Field(int, description="Splunk port", default_value=8089),
            "index": Field(str, description="Splunk index to use"),
            "username": Field(str, description="Splunk username", default_value="dino"),
            "password": Field(str, description="Splunk password", default_value="password")
        },
        "generate_orc_archives": {
            "source_path": Field(str, description="File or folder containing orc archive(s) SHOULD START WITH /DINO_ROOT"),
            'recurse': Field(bool, description='Whether or not to recurse subfolders', default_value=True),
            'file_magic': Field(str, description='Find ORC archives of a given file type', default_value="7-zip archive data"),
            'file_names_regexes': Field([str], description='Find ORC archives matching a specific regex', default_value=["^Collect_.*.7z"]),
        },
        "mft": {
            "archive_name_patterns" : Field([str], description="MFT Archive name pattern", default_value=["MFT.7z"]),
            "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
        },
        "autoruns": {
            "file_name_patterns": Field([str], description="Autoruns file name patterns", default_value=["*utorun*.csv"]),
            "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
        },
        "evtx": {
            "file_names_patterns": Field([str], description="EVTX file name patterns", default_value=["*.evtx", "*.evtx_data"]),
            "archive_name_patterns": Field([str], description="Archive name containing windows event logs", default_value=["Evtx.7z", "Event.7z", "Events.7z"]),
            "enabled": Field(bool, description="Whether or not to activate this module (this will also disable chainsaw)", default_value=True),
        },
        "hives": {
            "sam": {
                "archive_name_patterns": Field([str], description="Archive name containing SAM hives files", default_value=["SAM.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed SAM hives files", default_value=["*_data"]),
                "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
            },
            "system": {
                "archive_name_patterns": Field([str], description="Archive name containing SYSTEM hives files", default_value=["SystemHives.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed SYSTEM hives files", default_value=["*_data"]),
                "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
            },
            "user": {
                "archive_name_patterns": Field([str], description="Archive name containing USER hives files", default_value=["UserHives.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed USER hives files", default_value=["*_data"]),
                "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
            },
        },
        "ntfs": {
            "info": {
                "archive_name_patterns": Field([str], description="Archive name containing NTFSInfo files", default_value=["NTFSInfo.7z", "NTFSInfo_offline.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed NTFSInfo files", default_value=["NTFSInfo_*.csv"]),
                "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
            },
            "i30": {
                "archive_name_patterns": Field([str], description="Archive name containing NTFS $I30 files", default_value=["NTFSInfo_i30Info.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed $I30 files", default_value=["I30Info_*.csv"]),
                "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
            },
            "pehash": {
                "archive_name_patterns": Field([str], description="Archive name containing NTFS pehash files", default_value=["NTFSInfo_pehash.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed NTFS pehash files", default_value=["NTFSInfo_*.csv"]),
                "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
            },
            "secdescr" : {
                "archive_name_patterns": Field([str], description="Archive name containing NTFS secdescr files", default_value=["NTFSInfo_SecDesc.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed NTFS secdescr files", default_value=["SecDescr_*.csv"]),
                "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
            }
        },
        "usn": {
            "archive_name_patterns": Field([str], description="Archive name containing USN files", default_value=["USNInfo.7z"]),
            "file_names_patterns": Field([str], description="File pattern matching decompressed USN files", default_value=["USNInfo_*.csv"]),
            "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
        },
        "tcpvcon": {
            "file_names_patterns": Field([str], description="File pattern matching tcpvcon file", default_value=["Tcpvcon.txt", "tcpvcon.txt"]),
            "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
        },
        "listdlls": {
            "file_names_patterns": Field([str], description="File pattern matching listdlls file", default_value=["Listdlls.txt"]),
            "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
        },
        "psservice": {
            "file_names_patterns": Field([str], description="File pattern matching psservice file", default_value=["PsService.txt"]),
            "enabled": Field(bool, description="Whether or not to activate this module", default_value=True),
        }
    }
)
def orc_preset(val):
    return {
        "execution": {
            "config": val["celery_executor"]
        },
        "resources": {
            "splunk": {
                "config": {
                    "host": val["splunk"]["host"],
                    "port": val["splunk"]["port"],
                    "index": val["splunk"]["index"],
                    "password": val["splunk"]["password"],
                    "username": val["splunk"]["username"]
                }
            }
        },
        "ops": {
            "generate_orc_archives": {
                "config": val["generate_orc_archives"]
            },
            "mft_find_archive": {
                "config": {
                    "file_names_patterns": val["mft"]["archive_name_patterns"],
                    "skip": not val["mft"]["enabled"]
                }
            },
            "autoruns_send_files": {
                "config": {
                    "file_names_patterns": val["autoruns"]["file_name_patterns"],
                    "skip": not val["autoruns"]["enabled"]
                }
            },
            "process_chainsaw": {
                "config": {
                    "file_names_patterns": val["evtx"]["file_names_patterns"]
                }
            },
            "evtx_find_archive": {
                "config": {
                    "file_names_patterns": val["evtx"]["archive_name_patterns"],
                    "skip": not val["evtx"]["enabled"]
                }
            },
            "evtx_find_files": {
                "config": {
                    "file_names_patterns": val["evtx"]["file_names_patterns"],

                }
            },
            "hives_sam_find_archive": {
                "config": {
                    "file_names_patterns": val["hives"]["sam"]["archive_name_patterns"],
                    "skip": not val["hives"]["sam"]["enabled"]

                }
            },
            "hives_system_find_archive": {
                "config": {
                    "file_names_patterns": val[f"hives"]["system"]["archive_name_patterns"],
                    "skip": not val["hives"]["system"]["enabled"]
                }
            },
            "hives_user_find_archive": {
                "config": {
                    "file_names_patterns": val["hives"]["user"]["archive_name_patterns"],
                    "skip": not val["hives"]["user"]["enabled"]
                }
            },
            "ntfs_find_archive": {
                "config": {
                    "file_names_patterns": val["ntfs"]["info"]["archive_name_patterns"],
                    "skip": not val["ntfs"]["info"]["enabled"]
                }
            },
            "ntfs_i30_find_archive": {
                "config": {
                    "file_names_patterns": val["ntfs"]["i30"]["archive_name_patterns"],
                    "skip": not val["ntfs"]["i30"]["enabled"]
                }
            },
            "ntfs_pehash_find_archive": {
                "config": {
                    "file_names_patterns": val["ntfs"]["pehash"]["archive_name_patterns"],
                    "skip": not val["ntfs"]["pehash"]["enabled"]
                }
            },
            "ntfs_secdescr_find_archive": {
                "config": {
                    "file_names_patterns": val["ntfs"]["secdescr"]["archive_name_patterns"],
                    "skip": not val["ntfs"]["secdescr"]["enabled"]
                }
            },
            "usn_find_archive": {
                "config": {
                    "file_names_patterns": val["usn"]["archive_name_patterns"],
                    "skip": not val["usn"]["enabled"]
                }
            },
            "hives_system_find_files": {
                "config": {
                    "file_names_patterns": val["hives"]["system"]["file_names_patterns"],
                }
            },
            "hives_sam_find_files": {
                "config": {
                    "file_names_patterns": val["hives"]["system"]["file_names_patterns"],
                }
            },
            "hives_user_find_files": {
                "config": {
                    "file_names_patterns": val["hives"]["user"]["file_names_patterns"],
                }
            },
            "ntfs_send_files": {
                "config": {
                    "file_names_patterns": val["ntfs"]["info"]["file_names_patterns"],
                }
            },
            "ntfs_i30_send_files": {
                "config": {
                    "file_names_patterns": val["ntfs"]["i30"]["file_names_patterns"]
                }
            },
            "ntfs_pehash_send_files": {
                "config": {
                    "file_names_patterns": val["ntfs"]["pehash"]["file_names_patterns"]
                }
            },
            "ntfs_secdescr_send_files": {
                "config": {
                    "file_names_patterns": val["ntfs"]["secdescr"]["file_names_patterns"]
                }
            },
            "usn_send_files": {
                "config": {
                    "file_names_patterns": val["usn"]["file_names_patterns"]
                }
            },
            "tcpvcon_find_file": {
                "config": {
                    "file_names_patterns": val["tcpvcon"]["file_names_patterns"],
                    "skip": not val["tcpvcon"]["enabled"]
                }
            },
            "listdlls_find_file": {
                "config": {
                    "file_names_patterns": val["listdlls"]["file_names_patterns"],
                    "skip": not val["listdlls"]["enabled"]
                }
            },
            "psservice_find_file": {
                "config": {
                    "file_names_patterns": val["psservice"]["file_names_patterns"],
                    "skip": not val["psservice"]["enabled"]
                }
            }
        }
    }