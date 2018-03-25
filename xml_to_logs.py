# coding=utf-8

import lxml
import time
import argparse
from base import Base, engine, Session
from lxml import etree
from sqlalchemy import Column, Integer, String


class Backup(Base):
    __tablename__ = 'backup'
    id = Column(Integer, primary_key=True)
    body = Column(String(250), nullable=False)
    protocol = Column(String(250), nullable=False)
    address = Column(String(250), nullable=False)
    date = Column(String(250), nullable=False)
    readable_date = Column(String(250), nullable=False)
    type = Column(String(250), nullable=False)


def parser_cl():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=argparse.FileType('r'), help='Backup file you want to inspect.')
    args = parser.parse_args()
    return args


def xml_to_dict(xml):
    return dict([(item[0], item[1]) for item in xml.items()])


def get_xml_root(xml_file):
    parser = lmlx.etree.XMLParser(recover=True)
    tree = lmlx.etree.parse(xml_file, parser)
    return tree.getroot()


def json_to_b(json_data):
    item = Backup(body=json_data['body'], protocol=json_data['protocol'],
                  address=json_data['address'], date=json_data['date'],
                  readable_date=json_data['readable_date'],
                  type=json_data['type'])
    return item

def run():
    args = parser_cl()
    Base.metadata.create_all(engine)
    session = Session()
    root = get_xml_root(args.file)

    f = open('log', 'w')
    for i, sms in enumerate(root):
        json_data = xml_to_dict(sms)
        item = json_to_b(json_data)
        session.add(item)

        date = time.strftime("%D %H:%M", time.localtime(int(sms.get('date'))))
        sender = sms.get('contact_name').encode('utf-8') if sms.get('type') == '1' else 'Me'
        body = sms.get('body').encode('utf-8')
        line = '%s - %s : %s\n' % (date, sender, body)

        f.write(line)
    session.commit()
    smss = session.query(Backup).all()
    for sms in smss:
        print(sms.body)


if __name__ == '__main__':
    run()
