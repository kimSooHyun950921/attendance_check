import asyncio
import re
from datetime import datetime
import csv

FLAGS = None


async def client_handler(reader, writer):
    print(f'Connected with {writer.get_extra_info("peername")}')

    cdata = (await reader.read(1500)).decode('utf-8')
    print(f'{writer.get_extra_info("peername")} start attendance')

    writer.write("INPUT ID,NAME,CODE(format:ID,NAME,CODE): ".encode())
    cdata = (await reader.read(1500)).decode('utf-8')
    print(cdata)
    cdata = cdata.split(',')
    validity = check_validity(cdata[0], int(cdata[2]))

    if validity is not None:
      writer.write(validity.encode())
    else:
      writer.write("END".encode())
      store_student_info(cdata[0], cdata[1])
    
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
    if int(num) == 950921:
      return True
    return False


def check_validity(student_id, random_num):
    if check_randoms(random_num):
      if check_ID(student_id):
        return None
      else:
        return "check student ID"
    else:
      return "check random value"


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

