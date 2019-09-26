import asyncio
import json
import re
from  datetime import datetime
import csv
import urllib.parse
FLAGS = None


async def client_handler(reader, writer):
    print(f'Connected with {writer.get_extra_info("peername")}')
    cdata = (await reader.read(1500)).decode('utf-8')
    s_id = b''
    s_name = ''
    random_num = '' 
    sdata = ''

    try:
      cdata = cdata.split('\r\n')
      cmethod, cpath, cproto = cdata[0].split(' ')
      
      if cmethod == 'POST':
        jdata = json.loads(cdata[-1])
        s_id, s_name, random_num = do_post(jdata)
      elif cmethod == 'GET':
        s_id, s_name, random_num = do_get(cpath)
        print(s_id, s_name, random_num)
      
      err_msg = check_validity(s_id, random_num)
      print(err_msg)
      if err_msg:
        sdata = get_decline_data(err_msg)
      else:
        sdata = get_send_data(s_id, s_name, random_num)
        store_student_info(s_id, s_name)
         
    except Exception as e:
      print("ERROR", e)
      writer.close()

    print("SDATA", type(sdata))
#    sdata = sdata.encode('utf-8')
    writer.write(sdata)
    await writer.drain()
    writer.close()


def get_decline_data(err_msg):
    sdata = ('HTTP/1.1 200 OK\r\n'                                          
             'Content-Type: text/html; encoding=utf8\r\n'                   
             'Content-Length: 7\r\n'                                        
             'Connection: close\r\n'                                        
             '\r\n'                                                         
              +err_msg).encode('utf-8')  
    return sdata
    

def store_student_info(student_id, name):
    now = datetime.now()
    time = '%s-%s-%s %s:%s:%s' % \
           (now.year, now.month, now.day, now.hour, now.minute, now.second)
    print(time, student_id, name)
    with open('student2.csv','a', encoding='utf-8') as csv_file:
      csv_writer = csv.writer(csv_file, delimiter=',',
                              quotechar='|', quoting=csv.QUOTE_MINIMAL)
      csv_writer.writerow([time, student_id, name])


def do_post(cdata):
    student_id = cdata['student_id']
    student_name = cdata['student_name']
    random_num = cdata['random_num']
    print("s_name", student_name)
    return student_id, student_name, random_num


def get_send_data(s_id, s_name, ran_num):
    send_data_format = 'HTTP/1.1 200 OK\r\n'+\
                       'Content-Type: text/html; encoding=utf8\r\n'+\
                       'Content-Length: 6\r\n'+\
                       'Connection: close\r\n'+\
                       '\r\n'+\
                       '200 OK'+\
                       '{0}, {1}, {2}'.format(s_id, s_name, ran_num)
    send_data = send_data_format.encode('utf-8')
    print(send_data)
    return send_data


def do_get(cpath):
    print(cpath)
    split_cpath = cpath.split('&')
    student_id = split_cpath[0].split('=')[1]
    student_name = split_cpath[1].split('=')[1]
    random_num = split_cpath[2].split('=')[1]
    student_name = urllib.parse.unquote(student_name)
    return student_id, student_name, random_num


def check_validity(student_id, random_num):
    if check_randoms(random_num):
      if check_ID(student_id):
        return None
      else:
        return "check student ID"
    else:
      return "check random value"
    

def check_randoms(num):
    if int(num) == 51432:
      return True
    return False


def check_ID(student_id):
    p = re.compile("20[0-9]{2}0[0-9]{4}")
    is_match = p.match(student_id)
    if is_match:
      return True
    else:
      return False

 
def main(_):
    print(f'Parsed args {FLAGS}')
    print(f'Unparsed args {_}')

    # get event loop
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(client_handler,
                                '', FLAGS.port,
                                loop=loop,
                                reuse_address=True)
    server = loop.run_until_complete(coro)

    print('Start Server')
    try:
      loop.run_forever()
    except KeyboardInterrupt:
      print('End Server')

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8888,
                        help='Server port number')

    FLAGS, _ = parser.parse_known_args()

    main(_)

