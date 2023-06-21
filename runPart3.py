import os
import subprocess
from multiprocessing import Process
from collections import OrderedDict

os.system("kubectl delete jobs --all")

# ["blackscholes", "canneal", "dedup", "ferret", "freqmine", "radix", "vips"]
node2core = OrderedDict({"blackscholes":1})
node4core = OrderedDict({"ferret":4, "vips":4})
node8core = OrderedDict({"freqmine":4, "canneal":4, "dedup":4, "radix":4})

nodetypes = [node2core, node4core, node8core]
nodenames = ["node2core", "node4core", "node8core"]

nodecores = [2,4,8]
threadUsed = [0,0,0]
runnningJobs = [[], [], []]

def getCurrentSucceedJobs():
    cmd = "kubectl get jobs -o=jsonpath='{.items[?(@.status.succeeded==1)].metadata.name}'"
    output = subprocess.check_output(cmd, shell=True)
    current_jobs = output.decode("utf-8").split()
    return current_jobs

def change_file():
    for i in range(len(nodetypes)):
        for job, thread in nodetypes[i].items():
            # change yaml files

            # mac: 
            change_node_selector = r"sed -i '' 's/cca-project-nodetype: .*/cca-project-nodetype: \"%s\"/g' parsec-benchmarks/part2b/parsec-%s.yaml" % (nodenames[i], job)
            change_thread = r"sed -i '' 's/-n [0-9]*/-n %d/g' parsec-benchmarks/part2b/parsec-%s.yaml" % (thread, job)
            
            # linux: 
            # change_node_selector = r"sed -i 's/cca-project-nodetype: .*/cca-project-nodetype: \"%s\"/g' parsec-benchmarks/part2b/parsec-%s.yaml" % (nodenames[i], job)
            # change_thread = r"sed -i 's/-n [0-9]*/-n %d/g' parsec-benchmarks/part2b/parsec-%s.yaml" % (nodetypes[i][job], job)

            os.system(change_node_selector)
            os.system(change_thread)

def launch_job(i):
    # launch job
    for job, thread in nodetypes[i].items():
        launch_job = r"kubectl create -f ./parsec-benchmarks/part2b/parsec-%s.yaml" % (job)
        threadUsed[i] = threadUsed[i] + thread
        print("launch job in node ",nodenames[i],": ", job)
        print("used cores in node ",nodenames[i],": ", threadUsed[i])
        subprocess.run(launch_job, shell=True)
        runnningJobs[i].append("parsec-"+job)

        if(threadUsed[i] >= nodecores[i]):
            currentJobs = getCurrentSucceedJobs()
            print("current succeed jobs: ",currentJobs)
            for j in currentJobs:
                if(j in runnningJobs[i]):
                    runnningJobs[i].remove(j)

            print("current running jobs in node ",nodenames[i],": ",runnningJobs[i])

            while True:
                for elem in runnningJobs[i]:
                    if elem in getCurrentSucceedJobs():
                        print(elem,"completed!")
                        threadUsed[i] = threadUsed[i] - thread
                        break
                else:
                    continue
                break

if __name__ == '__main__':
    change_file()
    processes = []
    for i in range(len(nodetypes)):
        process = Process(target=launch_job, args=(i,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    print("All jobs have completed.")

    while(True):
        if(getCurrentSucceedJobs().sort() == ["parsec-blackscholes", "parsec-canneal", "parsec-dedup", "parsec-ferret", "parsec-freqmine", "parsec-radix", "parsec-vips"].sort()):
            break

    os.system("kubectl get pods -o json > results.json")
    os.system("python3 get_time.py results.json")
