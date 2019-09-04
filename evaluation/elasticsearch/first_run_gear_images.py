import sys
# package need to be installed, pip install docker
import docker 
import time
import yaml
import os
import random
import subprocess
import signal
import urllib2
import shutil
import xlwt
# package need to be installed, pip install elasticsearch
from elasticsearch import Elasticsearch

auto = False

private_registry = "202.114.10.146:9999/"
suffix = "-gear"

apppath = ""

# run paraments
hostPort = 9200
localVolume = ""
pwd = os.path.split(os.path.realpath(__file__))[0]

runEnvironment = ["discovery.type=single-node", ]
runPorts = {"9200/tcp": hostPort, "9300/tcp": 9300, }
runVolumes = {}
runWorking_dir = ""
runCommand = ""
waitline = "starting ..."

# result
result = [["tag", "finishTime", "local data", "pull data"], ]

class Runner:

    def __init__(self, images):  
        self.images_to_pull = images

    def check(self):
        # detect whether the file exists, if true, delete it
        if os.path.exists("./images_run.txt"):
            os.remove("./images_run.txt")
    
    def run(self):
        self.check()

        client = docker.from_env()
        # if don't give a tag, then all image under this registry will be pulled
        repos = self.images_to_pull[0]["repo"]

        for repo in repos:
            tags = self.images_to_pull[1][repo]
            for tag in tags:
                private_repo = private_registry + repo + suffix + ":" + tag

                if localVolume != "":
                    if os.path.exists(localVolume) == False:
                        os.makedirs(localVolume)

                print "start running: ", private_repo

                # create a random name
                runName = '%d' % (random.randint(1,100000000))

                # get present time
                startTime = time.time()

                # get present net data
                cnetdata = get_net_data()

                # run images
                container = client.containers.create(image=private_repo, environment=runEnvironment,
                                    ports=runPorts, volumes=runVolumes, working_dir=runWorking_dir,
                                    command=runCommand, name=runName, detach=True)

                container.start()

                while True:
                    if container.logs().find(waitline) >= 0:
                        break
                    else:
                        time.sleep(0.01)
                        pass

                while True:
                    if time.time() - startTime > 600:
                        break

                    try:
                        es = Elasticsearch(['localhost:9200'])
                        if es.ping() != True:
                            continue
                        b = {'name': 'three kingdom', "price": 355}
                        es.index(index='games', doc_type='game', body=b, id=1)
                        print "successfully create table games!"
                        print "successfully insert!"
                        print es.get(index='games', doc_type='game', id=1)
                        print es.delete(index='games', doc_type='game', id=1)
                        print "successfully delete!"
                        break
                    except:
                        time.sleep(0.1) # wait 100ms
                        pass
                        
                # print run time
                finishTime = time.time() - startTime

                print "finished in " , finishTime, "s"

                container_path = os.path.join("/var/lib/gear/private", private_repo)
                local_data = subprocess.check_output(['du','-sh', container_path]).split()[0].decode('utf-8')

                print "local data: ", local_data

                pull_data = get_net_data() - cnetdata

                print "pull data: ", pull_data

                print "\n"

                try: 
                    container.kill()
                except:
                    print "kill fail!"
                    pass

                container.remove(force=True)
                # cmd = '%s kill %s' % ("docker", runName)
                # rc = os.system(cmd)
                # assert(rc == 0)

                # record the image and its Running time
                result.append([tag, finishTime, local_data, pull_data])

                if auto != True: 
                    raw_input("Next?")
                else:
                    time.sleep(5)

                if localVolume != "":
                    shutil.rmtree(localVolume)

class Generator:
    
    def __init__(self, profilePath=""):
        self.profilePath = profilePath
    
    def generateFromProfile(self):
        if self.profilePath == "":
            print "Error: profile path is null"
        
        with open(self.profilePath, 'r') as f:
            self.images = yaml.load(f)

        return self.images

def get_net_data():
    netCard = "/proc/net/dev"
    fd = open(netCard, "r")

    for line in fd.readlines():
        if line.find("enp0s3") >= 0:
            field = line.split()
            data = float(field[1]) / 1024.0 / 1024.0

    fd.close()
    return data

if __name__ == "__main__":

    if len(sys.argv) == 2:
        auto = True

    generator = Generator(os.path.split(os.path.realpath(__file__))[0]+"/image_versions.yaml")

    images = generator.generateFromProfile()

    runner = Runner(images)

    runner.run()

    # create a workbook sheet
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("run_time")

    for row in range(len(result)):
        for column in range(len(result[row])):
            sheet.write(row, column, result[row][column])

    workbook.save(os.path.split(os.path.realpath(__file__))[0]+"/first_run.xls")