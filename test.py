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

import re
with open("/var/local/dino/DESKTOP/PsService.txt", "rb") as f:
    f = f.read().decode("ISO-8859-1")


for obj in f.split("SERVICE_NAME"):
    lines = obj.splitlines()
    if not lines or len(lines) < 4:
        continue
    item = {
        "service_name": lines[0].split(": ")[1],
        "display_name": lines[1].split(": ")[1],
        "description": lines[2]
    }
    check_dependencies = False
    for line in lines[3:]:
        line_stripped = line.strip()
        splited_line = [ i for i in line_stripped.split(":") if i]
        if len(splited_line) > 2:
            continue

        if check_dependencies:
            part = line_stripped.partition(":")
            if len(splited_line) == 1 and part[0] == "":
                item["dependencies"] = item["dependencies"] + ";" + part[2]
                continue
            else:
                check_dependencies = False
        if line_stripped.startswith("TYPE"):
            item["type"] = splited_line[1] if len(splited_line) > 1 else ""
        elif line_stripped.startswith("START_TYPE"):
            item["start_type"] = splited_line[1] if len(splited_line) > 1 else ""
        elif line_stripped.startswith("ERROR_CONTROL"):
            item["error_control"] = splited_line[1] if len(splited_line) > 1 else ""
        elif line_stripped.startswith("BINARY_PATH_NAME"):
            item["binary_path_name"] = splited_line[1] if len(splited_line) > 1 else ""
        elif line_stripped.startswith("TAG"):
            item["tag"] = splited_line[1] if len(splited_line) > 1 else ""

        elif line_stripped.startswith("DEPENDENCIES"):
            item["dependencies"] = splited_line[1] if len(splited_line) > 1 else ""
            check_dependencies = True
        elif line_stripped.startswith("TAG"):
            item["tag"] = splited_line[1] if len(splited_line) > 1 else ""
        elif line_stripped.startswith("FAIL_RESET_PERIOD"):
            item["fail_reset_period"] = splited_line[1] if len(splited_line) > 1 else ""

        elif line_stripped.startswith("SERVICE_START_NAME"):
            item["service_start_name"] = splited_line[1] if len(splited_line) > 1 else ""
        elif line_stripped.startswith("LOAD_ORDER_GROUP"):
            item["load_order_group"] = splited_line[1] if len(splited_line) > 1 else ""
    print(item)
