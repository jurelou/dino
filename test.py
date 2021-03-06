# import splunklib.client as client
# service = client.connect(host="localhost", username="dino", password="password", autologin=True)
# index = service.indexes["autoruns"]

# sock = index.attach(sourcetype="st", host="h", source="s")
# sock.send(b'sssss')
# sock.close()
# with index.attached_socket(sourcetype="st", host="h", source="s") as sock:
#     sock.send(b'ss')
#     sock.send(b'dd')

# from dino.utils.splunk import SplunkHEC

# with SplunkHEC(sourcetype="st", host="h", source="s", index="doesnotexists") as f:
#     f.send(b"mpl")

# import base64

# from Registry import Registry

# reg = Registry.Registry(
#     "/data/dino_root/__DINO_TEMP/Collect_DESKTOP-QESMCVM_20200114_152824_System_0c99690051fa43ef817c431b1bcb8872/UserHives_07754933515e42729d3ab3172f6b9dbe/0005000000015CFF_NTUSER.DAT_data"
# )


# def rec(key, depth=0):
#     # print("================================")
#     try:
#         # print(key.path(), key.name(), key.timestamp())
#         for v in key.values():
#             if v.value_type_str() == "RegBin":
#                 base64.b64encode(v.value()).decode("utf-8")
#     except Exception as err:
#         print("ERRR", err)

#     for subkey in key.subkeys():
#         rec(subkey, depth + 1)


# rec(reg.root())

# from dino.jobs.orc import orc
# import yaml

# def load_yaml_file(path):
#     with open(path, "r") as preset_file:
#         try:
#             return yaml.safe_load(preset_file)
#         except yaml.YAMLError as err:
#             print(f"Could not parse yaml file `{path}`.")
#     return None

# orc_preset = load_yaml_file("presets/orc.yaml")

# print(orc_preset)

# orc.execute_in_process({
#     "gather_orc_archives": {"source_path": "/DINO_ROOT"},
#     "splunk": {"index": "lol", "host": "localhost"}
# })