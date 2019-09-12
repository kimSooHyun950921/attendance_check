import asyncio
import re
import csv
import urllib.parse
from datetime import datetime
FLAGS = None


async def client_handler(reader, writer):
    #print(f'Connected with {writer.get_extra_info("peername")}')
    cdata = (await reader.read(1500)).decode('utf-8')
    sdata = ''
    try:
        cmethod, cpath, cproto = (cdata.split('\r\n')[0]).split(' ')
        #print(cmethod, cpath, cproto)

    #TODO 192로 시작하는지 확인하는 모듈
    #TODO 학번이 제대로 들어왔는지 확인하는 모듈
    #TODO 학번을 저장하는 모듈
    #TODO 출석 IP가 계속 들어와있는지 확인하는 모듈

        s_id, s_name, random_num = parsing_attendance(cpath)
        print("student_id:",s_id\
             ,"\nstudent_name:", s_name\
              ,"\nrandom_num", random_num)
        if not check_randoms(random_num):
          sdata = decline_message(cmethod, "Random Value Error")
          print("check_randoms", sdata)

        elif not check_ID(s_id):
          sdata = decline_message(cmethod, "ID ERROR")
          print("check_ID", sdata)

        else:
          sdata = confirm_message(cmethod)
          store_student_INFO(s_id, s_name)
          print("store_ok")
    
        writer.write(sdata)
        await writer.drain()
        writer.close()

    except Exception as e:
        writer.close()


def confirm_message(cmethod):
    if cmethod == 'GET':                                                        
      sdata = ('HTTP/1.1 200 OK\r\n'                                          
               'Content-Type: text/html; encoding=utf8\r\n'                   
               'Content-Length: 6\r\n'                                        
               'Connection: close\r\n'                                        
               '\r\n'                                                         
               'GET OK 출석완료').encode('utf-8')                                      
    elif cmethod == 'POST':
        sdata = ('HTTP/1.1 200 OK\r\n'                                          
                 'Content-Type: text/html; encoding=utf8\r\n'                   
                 'Content-Length: 7\r\n'                                        
                 'Connection: close\r\n'                                        
                 '\r\n'                                                         
                 'POST OK 출석완료').encode('utf-8')   
    return sdata


def decline_message(cmethod, err_msg):
    if cmethod == 'GET':
      sdata = ('HTTP/1.1 200 OK\r\n'
               'Content-Type: text/html; encoding=utf8\r\n'
               'Content-Length: 6\r\n'
               'Connection: close\r\n'
               '\r\n'
                +err_msg).encode('utf-8')
    elif cmethod == 'POST':
        sdata = ('HTTP/1.1 200 OK\r\n'
                 'Content-Type: text/html; encoding=utf8\r\n'
                 'Content-Length: 7\r\n'
                 'Connection: close\r\n'
                 '\r\n'
                 +err_msg).encode('utf-8')
    return sdata


def parsing_attendance(cpath):
    split_cpath = cpath.split('&')
    s_id = split_cpath[0].split('=')[1]
    s_name = split_cpath[1].split('=')[1]
    random_num = split_cpath[2].split('=')[1]
    s_name = urllib.parse.unquote(s_name)
    print(s_id, s_name, random_num)
    return s_id, s_name, random_num



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


def store_student_INFO(student_id, name):
    now = datetime.now()
    time = '%s-%s-%s %s:%s:%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    print(time, student_id, name)
    with open('student.csv','a', encoding='utf-8') as csv_file:
      csv_writer = csv.writer(csv_file, delimiter=',',
                              quotechar='|', quoting=csv.QUOTE_MINIMAL)
      csv_writer.writerow([time, student_id, name])


def check_IPs():
    pass


def main(_):
#    print(f'Parsed args {FLAGS}')
#    print(f'Unparsed args {_}')

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

