import asyncio
from datetime import datetime
import csv
import re

FLAGS = None


async def client_handler(reader, writer):
    print(f'Connected with {writer.get_extra_info("peername")}')
    send_list = ['input name', 'input ID', 'input passcode', "input OK"]
    recv_dict = {"name":'', "ID":'', "passcode":int()}

    cdata = (await reader.read(1500)).decode('utf-8')
    print("[{}]".format(writer.get_extra_info("peername")[0]), cdata)
    
    for send_word in send_list:
      info = send_word.split(' ')[1]
      writer.write(send_word.encode('utf-8'))

      cdata = (await reader.read(1500)).decode('utf-8')
      print("[{}]".format(writer.get_extra_info("peername")[0]), cdata)

      if not validity_check(cdata, info):
        writer.write("not correct try Again".encode('utf-8'))
        break
      recv_dict[info] = cdata

    store_student_info(recv_dict["ID"], recv_dict["name"])
    writer.write("bye".encode("utf-8"))


    await writer.drain()
    writer.close()


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
                                                                                
                                                                                
def validity_check(data, info):
    if info == "ID":
      return check_ID(data)
    elif info == "passcode":
      return check_randoms(data)
    else:
      return True
      
                                                                                
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

