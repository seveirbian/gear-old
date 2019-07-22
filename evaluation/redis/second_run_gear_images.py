import sys
# package need to be installed, pip install docker
import docker 
import time
import random
import yaml
import os
import subprocess
import signal
import urllib2

auto = False

private_registry = "202.114.10.146:9999/"
suffix = "-gearmd"

apppath = ""

# run paraments
hostPort = 8080
runEnvironment = []
runPorts = {"8080/tcp": hostPort,}
runVolumes = {}
runWorking_dir = ""
runCommand = ""



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

                print "start running: ", private_repo

                # create a random name
                runName = '%d' % (random.randint(1,100000000))

                # get present time
                startTime = time.time()

                # get present net data
                cnetdata = get_net_data()

                # run images
                try:
                    container = client.containers.create(image=private_repo, environment=runEnvironment,
                                        ports=runPorts, volumes=runVolumes, working_dir=runWorking_dir,
                                        command=runCommand, name=runName, detach=True)

                except docker.errors.NotFound:
                    print private_repo + " not found...\n\n"
                except docker.errors.ImageNotFound:
                    print private_repo + " image not fount...\n\n"

                container.start()

                while True:
                    if time.time() - startTime > 600:
                        break

                    try:
                        req = urllib2.urlopen('http://localhost:%d'%hostPort)
                        if req.read().find("All Rights Reserved") >= 0:
                            print "OK!"
                        req.close()
                        break
                    except:
                        time.sleep(0.01) # wait 10ms
                        pass

                # print run time
                finishTime = time.time() - startTime

                print "finished in " , finishTime, "s\n"

                print "pull data: ", get_net_data() - cnetdata

                try: 
                    container.kill()
                except:
                    print "kill fail!"
                    pass
                    
                container.remove(force=True)

                # record the image and its Running time
                self.record(private_repo, tag, finishTime)

                if auto != True: 
                    raw_input("Next?")
                else:
                    time.sleep(5)


    def record(self, repo, tag, time):
        with open("./images_run.txt", "a") as f:
            f.write("repo: "+str(repo)+" tag: "+str(tag)+" time: "+str(time)+"\n")

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

    fd.Close()
    return data

if __name__ == "__main__":

    if len(sys.argv) == 2:
        auto = True

    generator = Generator(os.path.split(os.path.realpath(__file__))[0]+"/image_versions.yaml")

    images = generator.generateFromProfile()

    runner = Runner(images)

    runner.run()