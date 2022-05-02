"""Collection of ORC jobs"""
from dagster_celery import celery_executor
from dagster import configured, job, op, DynamicOut, DynamicOutput, Any, get_dagster_logger, fs_io_manager
from uuid import uuid4
from dino.ops.artifacts.evtx import process_evtx
from dino.ops.artifacts.mft import process_mft
from dino.ops.artifacts.registry import process_registry
from dino.ops.artifacts.chainsaw import process_chainsaw
from dino.ops.artifacts.tcpvcon import process_tcpvcon
from dino.ops.artifacts.psservice import process_psservice
from dino.ops.artifacts.listdlls import process_listdlls

from dino.ops.decompress import decompress_file
from dino.ops.filesystem import find_file, generate_files, find_files
from dino.ops.splunk import send_csv_files, send_json_file
from dino.presets.orc import orc_preset
from dino.resources.splunk import splunk


@op(out=DynamicOut(Any))
def make_dynamic(items: Any):
    logger = get_dagster_logger()
    logger.info(f"Make dynamic output from {items}")
    for item in items:
        for sub in item:
            yield DynamicOutput(value=sub, mapping_key=uuid4().hex)

# @op
# def print_op(data):
#     logger = get_dagster_logger()
#     logger.info("==============================================================")
#     logger.info(f"PRINT OP: {data}")
#     logger.info("==============================================================")

@job(
    config=orc_preset,
    executor_def=celery_executor,
    resource_defs={
        "splunk": splunk,
        "io_manager": fs_io_manager.configured({"base_dir": "/var/local/dino_io_managers"})
    }
)
def orc():
    """Parse orc files."""
    generate_orc_archives = generate_files.alias("generate_orc_archives")
    orc_archives = generate_orc_archives().map(decompress_file)

    ###########################################################################################
    # LISTDLLS
    ###########################################################################################
    # CONFIGURE ops
    listdlls_find_file = find_file.alias("listdlls_find_file")

    # RUN pipeline
    orc_archives.map(listdlls_find_file).map(process_listdlls)

    ###########################################################################################
    # PSSERVICE
    ###########################################################################################
    # CONFIGURE ops
    psservice_find_file = find_file.alias("psservice_find_file")

    # RUN pipeline
    orc_archives.map(psservice_find_file).map(process_psservice)

    ###########################################################################################
    # TCPVCON
    ###########################################################################################
    # CONFIGURE ops
    tcpvcon_find_file = find_file.alias("tcpvcon_find_file")

    # RUN pipeline
    orc_archives.map(tcpvcon_find_file).map(process_tcpvcon)

    ###########################################################################################
    # MFT
    ###########################################################################################
    # CONFIGURE ops
    mft_find_archive = find_file.alias("mft_find_archive")
    mft_decompress_archive = decompress_file.alias("mft_decompress_archive")

    # RUN pipeline
    orc_archives.map(mft_find_archive).map(mft_decompress_archive).map(process_mft)

    ###########################################################################################
    # REGISTRY sam hives
    ###########################################################################################
    hives_sam_find_archive = find_file.alias("hives_sam_find_archive")
    hives_sam_decompress_archive = decompress_file.alias("hives_sam_decompress_archive")
    hives_sam_find_files = find_files.alias("hives_sam_find_files")
    hives_sam_process_file = process_registry.configured({
        "source": "sam_hives",
    }, name="hives_sam_process_file")

    sam_hives = orc_archives.map(hives_sam_find_archive).map(hives_sam_decompress_archive).map(hives_sam_find_files).collect()
    make_dynamic(sam_hives).map(hives_sam_process_file)

    ###########################################################################################
    # REGISTRY user hives
    ###########################################################################################
    hives_user_find_archive = find_file.alias("hives_user_find_archive")
    hives_user_decompress_archive = decompress_file.alias(
        "hives_user_decompress_archive"
    )
    hives_user_find_files = find_files.alias("hives_user_find_files")
    hives_user_process_file = process_registry.configured({
        "source": "user_hives",
    }, name="hives_user_process_file")


    user_hives = orc_archives.map(hives_user_find_archive).map(hives_user_decompress_archive).map(
        hives_user_find_files
    ).collect()
    make_dynamic(user_hives).map(hives_user_process_file)

    ###########################################################################################
    # REGISTRY system hives
    ###########################################################################################
    hives_system_find_archive = find_file.alias("hives_system_find_archive")
    hives_system_decompress_archive = decompress_file.alias(
        "hives_system_decompress_archive"
    )
    hives_system_find_files = find_files.alias("hives_system_find_files")
    hives_system_process_file = process_registry.configured({
            "source": "system_hives",
    }, name="hives_system_process_file")


    user_hives = orc_archives.map(hives_system_find_archive).map(
        hives_system_decompress_archive
    ).map(hives_system_find_files).collect()

    make_dynamic(user_hives).map(hives_system_process_file)

    ###########################################################################################
    # EVTX
    ###########################################################################################
    # CONFIGURE ops
    evtx_find_archive = find_file.alias("evtx_find_archive")
    evtx_decompress_archive = decompress_file.alias("evtx_decompress_archive")
    evtx_find_files = find_files.alias("evtx_find_files")

    # RUN main pipeline
    evtx_folders = orc_archives.map(evtx_find_archive).map(evtx_decompress_archive)

    # Run chainsaw
    evtx_folders.map(process_chainsaw)

    # Run evtx dump
    evtx_files = evtx_folders.map(evtx_find_files).collect()
    make_dynamic(evtx_files).map(process_evtx)

    ###########################################################################################
    # NTFS INFO
    ###########################################################################################
    # CONFIGURE ops
    ntfs_find_archive = find_file.alias("ntfs_find_archive")
    ntfs_decompress_archive = decompress_file.alias("ntfs_decompress_archive")

    @configured(send_csv_files, config_schema={"file_names_patterns": [str]})
    def ntfs_send_files(config):
        return {
            "file_names_patterns": config["file_names_patterns"],
            # "encoding": "utf-8",
            "source": "ntfs",
            "sourcetype": "dino:ntfs/json",
        }

    # RUN pipeline
    orc_archives.map(ntfs_find_archive).map(ntfs_decompress_archive).map(
        ntfs_send_files
    )

    ###########################################################################################
    # NTFS PEHASH
    ###########################################################################################
    # CONFIGURE ops
    ntfs_pehash_find_archive = find_file.alias("ntfs_pehash_find_archive")
    ntfs_pehash_decompress_archive = decompress_file.alias(
        "ntfs_pehash_decompress_archive"
    )

    @configured(send_csv_files, config_schema={"file_names_patterns": [str]})
    def ntfs_pehash_send_files(config):
        return {
            "file_names_patterns": config["file_names_patterns"],
            "source": "ntfs_pehash",
            # "encoding": "utf-8",
            "sourcetype": "dino:ntfs/json",
        }

    # RUN pipeline
    orc_archives.map(ntfs_pehash_find_archive).map(ntfs_pehash_decompress_archive).map(
        ntfs_pehash_send_files
    )

    ###########################################################################################
    # NTFS SECDESCR
    ###########################################################################################
    # CONFIGURE ops
    ntfs_secdescr_find_archive = find_file.alias("ntfs_secdescr_find_archive")
    ntfs_secdescr_decompress_archive = decompress_file.alias(
        "ntfs_secdescr_decompress_archive"
    )

    @configured(send_csv_files, config_schema={"file_names_patterns": [str]})
    def ntfs_secdescr_send_files(config):
        return {
            "file_names_patterns": config["file_names_patterns"],
            "source": "ntfs_secdescr",
            # "encoding": "utf-8",
            "sourcetype": "dino/json",
        }

    # RUN pipeline
    orc_archives.map(ntfs_secdescr_find_archive).map(
        ntfs_secdescr_decompress_archive
    ).map(ntfs_secdescr_send_files)

    ###########################################################################################
    # NTFS I30
    ###########################################################################################
    # CONFIGURE ops
    ntfs_i30_find_archive = find_file.alias("ntfs_i30_find_archive")
    ntfs_i30_decompress_archive = decompress_file.alias("ntfs_i30_decompress_archive")

    @configured(send_csv_files, config_schema={"file_names_patterns": [str]})
    def ntfs_i30_send_files(config):
        return {
            "file_names_patterns": config["file_names_patterns"],
            "source": "ntfs_i30",
            # "encoding": "utf-8",
            "sourcetype": "dino:ntfs:i30/json",
        }

    # RUN pipeline
    orc_archives.map(ntfs_i30_find_archive).map(ntfs_i30_decompress_archive).map(
        ntfs_i30_send_files
    )

    ###########################################################################################
    # USN INFO
    ###########################################################################################
    # CONFIGURE ops
    usn_find_archive = find_file.alias("usn_find_archive")
    usn_decompress_archive = decompress_file.alias("usn_decompress_archive")

    @configured(send_csv_files, config_schema={"file_names_patterns": [str]})
    def usn_send_files(config):
        return {
            "file_names_patterns": config["file_names_patterns"],
            "source": "usn",
            # "encoding": "utf-8",
            "sourcetype": "dino:usn/json",
        }

    # RUN pipeline
    orc_archives.map(usn_find_archive).map(usn_decompress_archive).map(usn_send_files)

    ###########################################################################################
    # Autoruns
    ###########################################################################################
    # CONFIGURE ops
    @configured(send_csv_files, config_schema={"file_names_patterns": [str], "skip": bool})
    def autoruns_send_files(config):
        return {
            "file_names_patterns": config["file_names_patterns"],
            "skip": config["skip"],
            "source": "autoruns",
            "encoding": "iso-8859-1",
            "sourcetype": "dino:autoruns/json",
        }

    # RUN pipeline
    orc_archives.map(autoruns_send_files)
