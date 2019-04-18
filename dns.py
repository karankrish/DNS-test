from pymongo import MongoClient
import json
from datetime import datetime
import mysql.connector
import logging
from logging.handlers import RotatingFileHandler
from datetime import timezone
from elasticsearch import Elasticsearch
import pythonwhois
from time import sleep
from confluent_kafka import Consumer


logging.basicConfig(filename='log/dnslog.log', level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger("dnslog.log")
handler = RotatingFileHandler("log/dnslog.log", maxBytes=2000, backupCount=25) 
if not logger: 
    logger.addHandler(handler)
with open('config.json') as f:
    config = json.load(f)
  

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def Main():
    consumer = Consumer({
    'bootstrap.servers': '192.168.100.80:9092',
    'group.id': 'dns',
    'client.id': 'sslcheck',
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 1000,
    'session.timeout.ms': 6000,
        'default.topic.config': {'auto.offset.reset': 'latest'}})
    consumer.subscribe(['domaindetails'])
    try:
        while True:
            msg = consumer.poll(0.1)
            if msg is None:
                continue
            elif not msg.error():
                try:
                    print('Received message: {0}'.format(msg.value()))
                    d=json.loads(msg.value())
                    print (d)
                    if d["featureConfig"]["domainMonitor"] == True:
                        print("true")
                        run((d["domainId"],d["companyDomain"]))
                    else:
                        pass
                    #elif d["job"] == "single":
                        #run((d["id"],d["domain"]))
                except:
                    pass
        else:
            print('Error occured: {0}'.format(msg.error().str()))

    except KeyboardInterrupt:
        pass

    finally:
        consumer.close()
    return


def run(key):
    
    ID=key[0]
    hostname=key[1]
    try:
        DomainExpiry_data=DomainExpiry(key)
        data={}
        data['_id']=ID
        data['hostname']=hostname
        data["LastUpdate"]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['DomainExpiry']=DomainExpiry_data
        msd(data)
       # elasticsearch(data)
    except Exception as e:
        logger.error("------run---------" +str(e))
        data={}
        data['_id']=ID
        data['hostname']=hostname
    #print(key[1])
    return 
    

def bulkrun():
    try:
        
        worker_data =  mySQL_read()    
        for i in worker_data:
            #threading.Thread(target=run, args = (i,)).start()
            run(i)
    except Exception as e:
        logger.error("------Main---------" +str(e))

    return 

def mySQL_read():
    try:
        asd=[]  
        mydb = mysql.connector.connect(
    	  host= config['mysql']['host'],
    	  user= config['mysql']['user'],
    	  passwd= config['mysql']['passwd'],
    	  database= config['mysql']['database']
    	)
        mycursor = mydb.cursor()
        mycursor.execute("SELECT company_domain, domain_id from login.client_domains")
        #mycursor.execute("SELECT user_reg_id,company_domain FROM registered_user limit 0,5")
        row = mycursor.fetchone()
        while row is not None:
            asd.append(row)
            row = mycursor.fetchone()
    except Exception as e:
        logger.error("------mySQL_read---------" +str(e))
        asd=[]

    return asd




def DomainExpiry(key):
    try:
        sleep(25)
        ID=key[0]
        hostname=key[1]
        details = pythonwhois.get_whois(hostname)
        t = details['expiration_date'][0]
        expiry_date=t.strftime('%m/%d/%Y')
        time=details['expiration_date'][0]
        expiry_time=time -datetime.now()
        registrar=details['registrar'][0]
        NS=details['nameservers']
        DEI=repr(expiry_time.days)
    except Exception as e:
        
        if str(e) != 'expiration_date':
            if (hostname.count('.') > 1):
                if hostname.find('.') != -1:
                    n= hostname.find('.')
                    domain_s=hostname[n+1:]
                    val=(ID, domain_s)    
                    return (DomainExpiry(val))
                else:
                    expiry_date=''
                    DEI=''
                    registrar=''
                    NS=''
            else:
                expiry_date=''
                DEI=''
                registrar=''
                NS=''
        else:
            logger.error(hostname +"--------DomainExpiry : ----------" + str(e))
            #return (DomainExpiry(key))
            expiry_date=''
            DEI=''
            registrar=''
            NS=''
    json_data={}
    json_data["domainexpiryDate"] = expiry_date
    json_data["domainDaysLeft"] = DEI
    json_data["registrar"]=registrar
    json_data["nameServer"]=NS
    return json_data









def msd(data):
    try:

        client =MongoClient(config['mongodb']['host'],
                                       username=config['mongodb']['username'],
                                       password=config['mongodb']['password'],
                                       authSource=config['mongodb']['authSource'])
        db = client.check
        collection = db.DomainExpiry12345
        x=data
        #collection.insert(x)
        collection.update({'_id': x['_id']},{'$set':x}, upsert=True, multi=False)

    except Exception as e:
        logger.error("---------Mongodb connection  :-------------- " +str(e))
    return 
def elasticsearch(data):
    try:
        data.pop("_id")
        es=Elasticsearch([{'host':'35.200.240.123','port':9200}])
        res = es.index(index='domainmonitor',doc_type='data',body=data)
    except Exception as e:
        logger.error("---------Elasticsearch  :-------------- " +str(e))
    return 
    
    

if __name__ == "__main__":
    Main()
    
   

