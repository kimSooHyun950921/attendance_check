import asyncio
import re
from datetime import datetime
import csv


FLAGS = None


async def client_handler(reader, writer):
    #print(f'Connected with {writer.get_extra_info("peername")}')
    cdata = (await reader.read(1500)).decode('utf-8')
    cpath = ''
    sdata = ''
    try:
        cmethod, cpath, cproto = (cdata.split('\r\n')[0]).split(' ')
    except:
        writer.close()

    if cmethod == 'GET':
        if cpath == '/favicon.ico':
          pass
        else:
          param = cpath.split('?')[1]
          param_list = param.split('&')

          name = param_list[0].split('=')[1]
          ID = param_list[1].split('=')[1]
          code = param_list[2].split('=')[1]


          validity = check_validity(ID, code)

          if validity is not None:
            sdata = get_sdata(True)
            store_student_info(ID, name)
          else:
            sdata = get_sdata(False)
            print("[ERROR] check ID or passing code")
          writer.write(sdata)
          await writer.drain()
        writer.close()


def get_sdata(is_check):
    sdata = ''
    if is_check == True:
      sdata = ('HTTP/1.1 200 OK\r\n'                                          
               'Content-Type: text/html; encoding=utf8\r\n'                   
               'Content-Length: 13\r\n'                                        
               'Connection: close\r\n'                                        
               '\r\n'                                                         
               'attendance OK').encode('utf-8')
    else:
      sdata = ('HTTP/1.1 200 OK\r\n'                                            
               'Content-Type: text/html; encoding=utf8\r\n'                     
               'Content-Length: 14\r\n'                                          
               'Connection: close\r\n'                                          
               '\r\n'                                                           
               'try again').encode('utf-8') 
    return sdata


def store_student_info(student_id, name):                                       
    now = datetime.now()                                                        
    time = '%s-%s-%s %s:%s:%s' % \
           (now.year, now.month, now.day, now.hour, now.minute, now.second)     
    print(time, student_id, name)                                               
    with open('student.csv','a', encoding='utf-8') as csv_file:                 
      csv_writer = csv.writer(csv_file, delimiter=',',                          
                              quotechar='|', quoting=csv.QUOTE_MINIMAL)         
      csv_writer.writerow([time, student_id, name])                             
                                                                                
                                                                                
def check_randoms(num):                                                         
    #print("[CHECK]", num)
    if int(num) == 6357:                                                      
      print("[CHECK]", num)
      return True   
    else:
      return False                                                                
                                                                                
                                                                                
def check_validity(student_id, random_num):                                     
    if check_randoms(random_num):                                               
      if check_ID(student_id):                                                  
        return None                                                             
      else:                                                                     
        return "check student ID"                                               
    else:                                                                       
      return None                                               
                                                                                
                                                                                
def check_ID(student_id):                                                       
    p = re.compile("20[0-9]{2}0[0-9]{4}")                                       
    is_match = p.match(student_id)                                              
    if is_match:                                                                
      return True                                                               
    else:                                                                       
      return False 

def main(_):
    #print(f'Parsed args {FLAGS}')
    #print(f'Unparsed args {_}')

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

