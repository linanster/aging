import copy
import json
import time
import datetime
import requests

from app.models import db_mysql, Testdata, TestdataArchive

from app.myglobal import RETENTION, gecloud_ip

from .mylogger import logger_cloud

def check_gecloud_connection():
    method = 'GET'
    ############################################
    url = "http://{}:5100/api/rasp/ping".format(gecloud_ip)
    ############################################
    headers = {}
    payload = {}
    try:
        response = requests.request(method=method, url=url, headers=headers, data=payload, timeout=10)
        # msg = response.content
        # msg = response.text
    except Exception as e:
        logger_cloud.error(str(e))
        return False
    else:
        # if response.ok and response.text == 'pong':
        if response.ok and response.json().get('msg') == 'pong':
            return True
        else:
            return False

def check_upgrade_pin(pin):
    ############################################
    url = 'http://{}:5100/api/rasp/verifypin'.format(gecloud_ip)
    ############################################
    payload = 'pin={}'.format(pin)
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data = payload)
    return response.json().get('verified')

    

def upload_to_cloud():
    logger_cloud.info('upload_to_cloud: start')
    # 0. check network status
    if not check_gecloud_connection():
        logger_cloud.error('upload_to_cloud: connection error')
        return 1

    try:
        # 1. fetch data from database
        # datas_raw = TestdataArchive.query.all()
        datas_raw = TestdataArchive.query.filter_by(bool_uploaded=False).all()
        datas_rdy = list()
        for item in datas_raw:
            entry = copy.deepcopy(item.__dict__)
            entry.pop('_sa_instance_state')
            entry.pop('id')
            datetime_obj = entry.get('datetime')
            datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
            datetime_dict = {'datetime': datetime_str}
            bool_uploaded_dict = {'bool_uploaded': True}
            entry.update(datetime_dict)
            entry.update(bool_uploaded_dict)
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
        method = 'PUT'
        ############################################
        url = "http://{}:5100/api/rasp/upload".format(gecloud_ip)
        ############################################
        headers = {
            'Authorization': 'Basic dXNlcjE6MTIzNDU2',
            'Content-Type': 'application/x-www-form-urlencoded',
            # 'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = json.dumps(request_msg)
        
        # 4. send request
        response = requests.request(method=method, url=url, headers=headers, data=payload, timeout=60)
        
        # 5. take response
        response_msg = response.json()
   
    except Exception as e:
        logger_cloud.error('upload_to_cloud: exception when uploading data to cloud')
        logger_cloud.error(str(e))
        return 5
    

    # 6. error handler
    if response_msg.get('errno') == 1:
        logger_cloud.error('upload_to_cloud: response errno error')
        return 2
    if response_msg.get('pin') != pin:
        logger_cloud.error('cloud_to_cloud: pin mismatch error')
        return 3

    # 7. save data entries into database
    try:
        for item in datas_raw:
            item.bool_uploaded = True
            db_mysql.session.add(item)
    except Exception as e:
        db_mysql.session.rollback()
        logger_cloud.error('upload_to_cloud: exception when updating database field bool_uploaded')
        logger_cloud.error(str(e))
        return 4
    else:
        db_mysql.session.commit()
        logger_cloud.info('upload_to_cloud: success(count: {})'.format(len(datas_raw)))
        return 0


def purge_local_archive():
    logger_cloud.info('purge_local_archive: start')
    # items = TestdataArchive.query.all()
    items = TestdataArchive.query.filter_by(bool_uploaded=True).all()
    d_now = datetime.datetime.now()
    count = 0
    try:
        for item in items:
            d_item = item.datetime
            # retention switch between production and test
            # (a)production requirement
            day_range = (d_now - d_item).days
            # (b)test convenience
            # day_range = (d_now - d_item).seconds
            if day_range > RETENTION:
                db_mysql.session.delete(item)
                count += 1
    except Exception as e:
        db_mysql.session.rollback()
        logger_cloud.error('purge_local_archive: exception')
        logger_cloud.error(str(e))
        return 1
    else:
        db_mysql.session.commit()
        logger_cloud.info('purge_local_archive: success(count: {})'.format(count))
        return 0
    
