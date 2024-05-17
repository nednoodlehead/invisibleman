import sqlite3
from util.data_types import InventoryObject, TableObject


def fetch_all() -> [InventoryObject]:
    return_list = []
    with sqlite3.connect("main.db") as conn:
        data = conn.execute("SELECT * FROM main")
        for item in data:
            return_list.append(InventoryObject(*item))
    return return_list


def fetch_all_enabled():  # [InventoryObject] without the enabled field
    return_list = []
    with sqlite3.connect("main.db") as conn:
        data = conn.execute(
            """
            SELECT assettype, manufacturer, serial, model, cost, assignedto, assetlocation, assetcategory,
            deploymentdate, replacementdate, retirementdate, notes, uniqueid FROM main WHERE status = 1;
            """
        )
        for item in data:
            return_list.append(item)
    return return_list


def fetch_all_enabled_for_table() -> [TableObject]:
    return_list = []
    # RETIRED = 1
    # NOT RETIRED = 0
    with sqlite3.connect("main.db") as conn:
        data = conn.execute(
            """
            SELECT assettype, manufacturer, serial, model, cost, assignedto, assetlocation, assetcategory,
            deploymentdate, replacementdate, retirementdate, notes, status, uniqueid FROM main WHERE status = 0
            """
        )
        for item in data:
            return_list.append(TableObject(*item))
    return return_list


def fetch_all_for_table() -> [TableObject]:
    return_list = []
    with sqlite3.connect("main.db") as conn:
        data = conn.execute(
            """
            SELECT assettype, manufacturer, serial, model, cost, assignedto, assetlocation, assetcategory,
            deploymentdate, replacementdate, retirementdate, notes, status, uniqueid FROM main
            """
        )
        for item in data:
            return_list.append(TableObject(*item))
    return return_list


# should only ever be called from a noteswindow being create, always with valid uuid.
def fetch_notes_from_uuid(uuid: str) -> str:
    with sqlite3.connect("main.db") as conn:
        data = conn.execute("SELECT notes FROM main WHERE uniqueid = ?", [uuid])
    return data.fetchone()[0]  # grab the only option


def fetch_from_uuid_to_update(uuid: str) -> InventoryObject:
    with sqlite3.connect("main.db") as conn:
        data = conn.execute("SELECT * FROM main WHERE uniqueid = ?", [uuid])
    processed = data.fetchone()
    obj = InventoryObject(*processed)
    return obj


def fetch_obj_from_retired():
    ret_list = []
    with sqlite3.connect("main.db") as conn:
        # remember. 1 = retired
        data = conn.execute(
            """
            SELECT assettype, manufacturer, serial, model, cost, assignedto,
            assetlocation, assetcategory, deploymentdate, replacementdate, 
            notes, uniqueid FROM main
            WHERE status = 1 
            """,
        )
    for item in data:
        ret_list.append(item)
    return ret_list


def fetch_obj_from_loc(location):
    ret_list = []
    with sqlite3.connect("main.db") as conn:
        data = conn.execute(
            """
            SELECT assettype, manufacturer, serial, model, cost, assignedto,
            assetlocation, assetcategory, deploymentdate,
            retirementdate, notes FROM main
            WHERE status = 0 AND assetlocation = ?
            """,
            (location,),
        )
    for item in data:
        ret_list.append(item)
    return ret_list


def fetch_retired_assets(year: str):
    ret_list = []
    with sqlite3.connect("main.db") as conn:
        print(year, type(year))
        data = conn.execute(
            """
            SELECT assettype, manufacturer, serial, model, cost, assignedto,
            assetlocation, assetcategory, deploymentdate,
            retirementdate, notes FROM main
            WHERE replacementdate <= ? AND status = 0
            """, (year,)
        )
    for item in data:
        print("FOUNDER")
        ret_list.append(item)
    return ret_list
