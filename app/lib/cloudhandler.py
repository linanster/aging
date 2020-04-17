import copy
import json
import time
import datetime
import requests

from app.models import db, Testdata, TestdataArchive

from app.myglobal import RETENTION

def check_cloud_connection():
    method = 'GET'
    ############################################
    url = "http://10.30.30.101:8000/ping"
    ############################################
    headers = {}
    payload = {}
    try:
        response = requests.request(method=method, url=url, headers=headers, data=payload, timeout=20)
        # msg = response.content
        # msg = response.text
    except Exception as e:
        print(str(e))
        return False
    else:
        if response.ok and response.text == 'pong':
            return True
        else:
            return False
    

def upload_to_cloud():
    # 1. fetch data from database
    datas_raw = TestdataArchive.query.all()
    datas_rdy = list()
    for item in datas_raw:
        entry = copy.deepcopy(item.__dict__)
        entry.pop('_sa_instance_state')
        entry.pop('id')
        datetime_obj = entry.get('datetime')
        datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        datetime_dict = {'datetime': datetime_str}
        is_sync_dict = {'is_sync': True}
        entry.update(datetime_dict)
        entry.update(is_sync_dict)
        datas_rdy.append(entry)

    # 2. assemble api request message
    request_msg = dict()
    pin = str(time.time())
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')    
    dict_pin = {'pin': pin}
    dict_timestamp = {'timestamp': timestamp}
    dict_data = {'testdatas': datas_rdy}
    request_msg.update(dict_pin)
    request_msg.update(dict_timestamp)
    request_msg.update(dict_data)

    # 3. send message via http post method
    method = 'POST'
    ############################################
    url = "http://10.30.30.101:8000/upload"
    ############################################
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    payload = json.dumps(request_msg)
    
    # 4. send request
    response = requests.request(method=method, url=url, headers=headers, data=payload)
    
    # 5. take response
    response_msg = response.json()

    # 6. error handler
    if response_msg.get('errno') == 1:
        print('error errno')
        return 1
    if response_msg.get('pin') != pin:
        print('error pin')
        return 2

    # 7. save data entries into database
    try:
        for item in datas_raw:
            item.is_sync = True
            db.session.add(item)
    except Exception as e:
        print(str(e))
        db.session.rollback()
        print('error when updating is_sync')
        return 3
    else:
        db.session.commit()
        print('success')
        return 0


def purge_local_archive():
    items = TestdataArchive.query.all()
    d_now = datetime.datetime.now()
    try:
        for item in items:
            d_item = item.datetime
            day_range = (d_now - d_item).days
            if day_range >= RETENTION:
                db.session.delete(item)
    except exception as e:
        db.session.rollback()
        print(str(e))
        print('error')
        return 1
    else:
        db.session.commit()
        print('success')
        return 0
    
