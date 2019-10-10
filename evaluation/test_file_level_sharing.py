import os
import hashlib

path = "/var/lib/docker/overlay2/"
hash_set = {}
storage = 0

def summary():
    print "files under %s\n"%path
    print "file number: %d\n"%len(hash_set)
    print "storage size: %d\n"%storage

def add_size(name):
    global storage
    fsize = os.path.getsize(name)
    fsize = fsize/float(1024*1024)
    storage += fsize

def insert(hash_value):
    if hash_set.has_key(hashlib) == False:
        hash_set[hash_value] = True
        return True
    return False

def calculate(name):
    f = open(name)
 
    thehash = hashlib.md5()

    theline = f.readline()
     
    while(theline):
        thehash.update(theline)
        theline = f.readline()

    return thehash.hexdigest()

def traverse(path):
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                name = os.path.join(root, file)
                if os.path.isfile(name) and os.path.islink(name):
                    hash_value = calculate(name)
                    if insert(hash_value) == True:
                        add_size(name)

if __name__ == "__main__":
    traverse(path)
    summary()