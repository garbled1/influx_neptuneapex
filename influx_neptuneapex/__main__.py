#!/usr/bin/env python3

try:
    import simplejson as json
except ImportError:
    import json
import requests
from requests.auth import HTTPBasicAuth
import base64
import argparse
import time
from influxdb import InfluxDBClient


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Hostname or IP of APEX",
                        required=True)
    parser.add_argument("--user", help="Apex Username", default="admin")
    parser.add_argument("--password", help="Apex Password", default="1234")
    parser.add_argument("--file", help="Read json file, not connect",
                        action='store', default=None)
    parser.add_argument('-i', '--influx_host', type=str, action='store',
                        default='127.0.0.1',
                        help='hostname of influx db (127.0.0.1)')
    parser.add_argument('-p', '--influx_port', type=int, action='store',
                        default=8086,
                        help='port number of influx db (8086)')
    parser.add_argument('--influx_user', type=str, action='store',
                        default=None,
                        help='InfluxDB username')
    parser.add_argument('--influx_pass', type=str, action='store',
                        default=None,
                        help='InfluxDB password')
    parser.add_argument('-d', '--influx_db', type=str, action='store',
                        default='apex',
                        help='InfluxDB database name (default: apex)')
    parser.add_argument('--poll_time', type=int, action='store',
                        default=60,
                        help='How often in seconds to poll the apex (60)')

    args = parser.parse_args()
    return args


def parse_apex(jdata):
    # First, grab the hostname
    hostname = jdata['istat']['hostname']

    # set a now
    now_sec = jdata['istat']['date']

    influx_data_json = []

    # now, the inputs
    for idx,input in enumerate(jdata['istat']['inputs']):
        point = {
            "measurement": "neptune_apex",
            "time": now_sec,
            "tags": {
                "hostname": hostname,
                "stat_type": "input",
                "type": input['type'],
                "name": input['name'],
                "did": input['did']
            },
            "fields": {
                "value": float(input['value'])
            }
        }
        influx_data_json.append(point)

    # now the outputs
    for idx,output in enumerate(jdata['istat']['outputs']):
        o_field = {}
        if output['type'] == 'variable' or output['type'] == 'serial':
            o_field['profile'] = output['status'][0]
            if output['status'][1] == '':
                o_field['value'] = 0.0
            else:
                o_field['value'] = float(output['status'][1])
            o_field['state'] = output['status'][2]

        elif output['type'] == 'alert' or output['type'] == 'outlet' or output['type'] == '24v' or output['type'] == 'virtual' or output['type'] == 'afs':
            if 'A' in output['status'][0]:
                o_field['auto'] = 1
            if 'ON' in output['status'][0]:
                o_field['value'] = 1.0
            elif 'OF' in output['status'][0]:
                o_field['value'] = 0.0
            o_field['state'] = output['status'][2]

        elif 'cor' in output['type']:
            o_field['state'] = output['status'][2]
            o_field['rpm'] = float(output['status'][4])
            o_field['temp'] = float(output['status'][5])
            o_field['watts'] = float(output['status'][6])
            o_field['value'] = float(output['status'][1])

        elif output['type'] == 'wav':
            o_field['profile'] = output['status'][0]
            o_field['state'] = output['status'][2]
            o_field['value'] = float(output['status'][1])
            o_field['flow'] = float(output['status'][6])
            o_field['rpm'] = float(output['status'][4])
            o_field['temp'] = float(output['status'][5])
            
        point = {
            "measurement": "neptune_apex",
            "time": now_sec,
            "tags": {
                "hostname": hostname,
                "stat_type": "output",
                "type": output['type'],
                "name": output['name'],
                "ID": output['ID'],
                "did": output['did']
            },
            "fields" : o_field
        }
        influx_data_json.append(point)
    return(influx_data_json)


def main(args=None):
    args = parse_arguments()

    try:
        if args.influx_user and args.influx_pass:
            db_client = InfluxDBClient(host=args.influx_host,
                                       port=args.influx_port,
                                       username=args.influx_user,
                                       password=args.influx_pass)
        else:
            db_client = InfluxDBClient(host=args.influx_host,
                                       port=args.influx_port)
    except:
        print("Cannot connect to InfluxDB!")
        return(1)

    try:
        db_client.switch_database(args.influx_db)
    except:
        print("Cannot find db named {0}, please create".format(args.influx_db))
        return(1)

    if args.file is not None:
        with open(args.file) as infile:
            json_data = json.load(infile)
    else:
        url = 'http://' + args.host + '/cgi-bin/status.json'

        while(True):
            try:
                req = requests.get(url, auth=(args.user, args.password))
                # print(req)
                json_data = req.json()
                # print(json_data)
                influxdata = parse_apex(json_data)
                try:
                    db_client.write_points(influxdata, time_precision='s')
                except Exception as e:
                    print("Cannot contact influx: {0}".format(str(e)))
                    exit(1)
            except Exception as e:
                print("Connection failed on {0} : {1}".format(str(url), str(e)))
                pass
            time.sleep(args.poll_time)


if __name__ == "__main__":
    main()
