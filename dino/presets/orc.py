from dagster import Field, config_mapping


@config_mapping(
    config_schema={
        "splunk": {
            "host": Field(str, description="Splunk hostname", default_value="splunk"),
            "port": Field(int, description="Splunk port", default_value=8089),
            "index": Field(str, description="Splunk index to use"),
            "username": Field(str, description="Splunk username", default_value="dino"),
            "password": Field(str, description="Splunk password", default_value="password")
        },
        "gather_orc_archives": {
            "source_path": Field(str, description="File or folder containing orc archive(s)", default_value="/DINO_ROOT"),
            'recurse': Field(bool, description='Whether or not to recurse subfolders', default_value=True),
            'file_magic': Field(str, description='Find ORC archives of a given file type', default_value="7-zip archive data"),
            'file_name_regex': Field(str, description='Find ORC archives matching a specific regex', default_value="^Collect_.*.7z"),
        },
        "mft": {
            "archive_name_patterns" : Field([str], description="MFT Archive name pattern", default_value=["MFT.7z"]),
        },
        "autoruns": {
            "file_name_patterns": Field([str], description="Autoruns file name patterns", default_value=["*utorun.csv", "*utoruns.csv"]),
        },
        "zircolite": {
            "files_extension": Field(str, description="Evtx files extension (used by zircolite)", default_value="evtx_data"),
        },
        "evtx": {
            "archive_name_patterns": Field([str], description="Archive name containing windows event logs", default_value=["Evtx.7z", "Event.7z", "Events.7z"]),
        },
        "hives": {
            "sam": {
                "archive_name_patterns": Field([str], description="Archive name containing SAM hives files", default_value=["SAM.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed SAM hives files", default_value=["*_data"])
            },
            "system": {
                "archive_name_patterns": Field([str], description="Archive name containing SYSTEM hives files", default_value=["SystemHives.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed SYSTEM hives files", default_value=["*_data"])
            },
            "user": {
                "archive_name_patterns": Field([str], description="Archive name containing USER hives files", default_value=["UserHives.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed USER hives files", default_value=["*_data"])
            },
        },
        "ntfs": {
            "info": {
                "archive_name_patterns": Field([str], description="Archive name containing NTFSInfo files", default_value=["NTFSInfo.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed NTFSInfo files", default_value=["NTFSInfo_*.csv"])
            },
            "i30": {
                "archive_name_patterns": Field([str], description="Archive name containing NTFS $I30 files", default_value=["NTFSInfo_i30Info.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed $I30 files", default_value=["I30Info_*.csv"])
            },
            "pehash": {
                "archive_name_patterns": Field([str], description="Archive name containing NTFS pehash files", default_value=["NTFSInfo_pehash.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed NTFS pehash files", default_value=["NTFSInfo_*.csv"])
            },
            "secdescr" : {
                "archive_name_patterns": Field([str], description="Archive name containing NTFS secdescr files", default_value=["NTFSInfo_SecDesc.7z"]),
                "file_names_patterns": Field([str], description="File pattern matching decompressed NTFS secdescr files", default_value=["SecDescr_*.csv"])
            }
        },
        "usn": {
            "archive_name_patterns": Field([str], description="Archive name containing USN files", default_value=["USNInfo.7z"]),
            "file_names_patterns": Field([str], description="File pattern matching decompressed USN files", default_value=["USNInfo_*.csv"])
        }

    }
)
def orc_preset(val):
    return {
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
            "gather_orc_archives": {
                "config": val["gather_orc_archives"]
            },
            "mft_find_archive": {
                "config": {
                    "file_names_patterns": val["mft"]["archive_name_patterns"]
                }
            },
            "autoruns_send_files": {
                "config": {
                    "file_names_patterns": val["autoruns"]["file_name_patterns"]
                }
            },
            "process_zircolite": {
                "config": {
                    "file_extension": val["zircolite"]["files_extension"]
                }
            },

            "evtx_find_archive": {
                "config": {
                    "file_names_patterns": val["evtx"]["archive_name_patterns"]
                }
            },
            "hives_sam_find_archive": {
                "config": {
                    "file_names_patterns": val["hives"]["sam"]["archive_name_patterns"]
                }
            },
            "hives_system_find_archive": {
                "config": {
                    "file_names_patterns": val["hives"]["system"]["archive_name_patterns"]
                }
            },
            "hives_user_find_archive": {
                "config": {
                    "file_names_patterns": val["hives"]["user"]["archive_name_patterns"]
                }
            },
            "ntfs_find_archive": {
                "config": {
                    "file_names_patterns": val["ntfs"]["info"]["archive_name_patterns"]
                }
            },
            "ntfs_i30_find_archive": {
                "config": {
                    "file_names_patterns": val["ntfs"]["i30"]["archive_name_patterns"]
                }
            },
            "ntfs_pehash_find_archive": {
                "config": {
                    "file_names_patterns": val["ntfs"]["pehash"]["archive_name_patterns"]
                }
            },
            "ntfs_secdescr_find_archive": {
                "config": {
                    "file_names_patterns": val["ntfs"]["secdescr"]["archive_name_patterns"]
                }
            },
            "usn_find_archive": {
                "config": {
                    "file_names_patterns": val["usn"]["archive_name_patterns"]
                }
            },

            "hives_sam_process_files": {
                "config": {
                    "file_names_patterns": val["hives"]["sam"]["file_names_patterns"]
                }
            },
            "hives_system_process_files": {
                "config": {
                    "file_names_patterns": val["hives"]["system"]["file_names_patterns"]
                }
            },
            "hives_user_process_files": {
                "config": {
                    "file_names_patterns": val["hives"]["user"]["file_names_patterns"]
                }
            },
            "ntfs_send_files": {
                "config": {
                    "file_names_patterns": val["ntfs"]["info"]["file_names_patterns"]
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
            }
        }
    }