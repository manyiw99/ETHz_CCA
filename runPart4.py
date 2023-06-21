'''
1. qps < 40k : 3 core - freqmine, ferret, blachsholes, canneal, vips, radix, dedup
2. 40k < qps < 80k : 3 core - blackscholes, canneal, vips, radix, dedup
                     2 core - ferret, freqmine
3. qps > 80k: 2 core - dedup, radix, vips, canneal, blackscholes, ferret, freqmine

cpu utlization:
memcached 1 core: 40k - 45, 80k - 90
'''

from collections import OrderedDict
import time
import psutil
import os
from enum import Enum
from scheduler_logger import SchedulerLogger,Job

import docker

client = docker.from_env()

class AllJob(Enum):
    MEMCACHED = "memcached"
    BLACKSCHOLES = "blackscholes"
    CANNEAL = "canneal"
    DEDUP = "dedup"
    FERRET = "ferret"
    FREQMINE = "freqmine"
    RADIX = "radix"
    VIPS = "vips"

class JobStatus(Enum):
    WAITING = "waiting"
    RUNNING = "running"
    PAUSED = "paused"
    EXITED = "exited"
    RECORDED = "recorded"

jobList = OrderedDict({
    AllJob.FREQMINE.value: JobStatus.WAITING.value,
    AllJob.FERRET.value: JobStatus.WAITING.value,
    AllJob.BLACKSCHOLES.value: JobStatus.WAITING.value,
    AllJob.CANNEAL.value: JobStatus.WAITING.value,
    AllJob.VIPS.value: JobStatus.WAITING.value,
    AllJob.RADIX.value: JobStatus.WAITING.value,
    AllJob.DEDUP.value: JobStatus.WAITING.value
}) # jobList_3cores
jobList_2cores = [AllJob.DEDUP.value, AllJob.RADIX.value, AllJob.VIPS.value, AllJob.CANNEAL.value, AllJob.BLACKSCHOLES.value, AllJob.FERRET.value, AllJob.FREQMINE.value]

previous_job_cores = OrderedDict({
    AllJob.FREQMINE.value: 3,
    AllJob.FERRET.value: 3,
    AllJob.BLACKSCHOLES.value: 3,
    AllJob.CANNEAL.value: 3,
    AllJob.VIPS.value: 3,
    AllJob.RADIX.value: 3,
    AllJob.DEDUP.value: 3
})

for job in jobList_2cores:
    try:
        os.system(f"sudo docker rm -f {job}")
    except:
        print("Deletion error")

os.system(f'pgrep memcached|xargs -n 1 sudo taskset -a -cp 0')
memcached_core =  1 # 1: user 1 core, core 0;  2: use 2 cores, core 0 and 1
memcachedState = -1 # -1: <40k 0: 40k-80k 1:>80k

countNum = 0

logger = SchedulerLogger()

def monitorMemcached(): 
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)

    if(memcached_core == 1):
        cpu = cpu_percent[0]
        if cpu <= 45:
            memcachedState = -1
        elif(cpu>45 and cpu<90):
            memcachedState = 0
        elif(cpu>=90):
            memcachedState = 1
        else:
            print("cpu calculation error!")

    if(memcached_core == 2):
        cpu = cpu_percent[0] + cpu_percent[1]
        if(cpu<=45):
            memcachedState = -1
        elif(cpu>45 and cpu<=130):
            memcachedState = 0
        elif(cpu>130):
            memcachedState = 1
        else:
            print("cpu calculation error!")

    print("previous memcached cores: ",memcached_core)
    print("current cpu: ",cpu,"-------- ",int(time.time()))
    print("memcached state: ",memcachedState)

    return memcachedState


def run_job(job):
    if(job == "radix"):
        client.containers.run(f"anakli/cca:splash2x_{job}",detach=True,cpuset_cpus=f"{str(memcached_core)}-3",name=job, command = f"./run -a run -S splash2x -p {job} -i native -n 2")
  
    else:
        client.containers.run(f"anakli/cca:parsec_{job}",detach=True, cpuset_cpus=f"{str(memcached_core)}-3", name=job,command = f"./run -a run -S parsec -p {job} -i native -n 2")
       
    logger.job_start(Job._value2member_map_.get(job),list(range(memcached_core,4)),2)
    jobList[job] = JobStatus.RUNNING.value
    print("run job: ",job)


def unpause_jobs(job):
    container = client.containers.get(job)
    container.reload()
    print("find unpause job: ",job," - ",container.attrs['State']['Status'])
    updateJobStatus()
    # if(container.attrs['State']['Status'] == "exited"):
    #     print("in unpause exited: ",job)
    #     jobList[job] = JobStatus.RECORDED.value
                
    #     logger.job_end(Job._value2member_map_.get(job))
    #     print(job," end!")
    if(jobList[job]==JobStatus.PAUSED.value):
        container.unpause()
        logger.job_unpause(Job._value2member_map_.get(job))
        print("unpause job: ",job)
        print('******** ',previous_job_cores[job],"   ",4-memcached_core)
        if(previous_job_cores[job]!=4-memcached_core):
            change_cores(job)
            print("change core after unpause: ",job)

def change_cores(job):
    container = client.containers.get(job)
    container.reload()
    container.update(cpuset_cpus=f"{str(memcached_core)}-3")
    
    logger.update_cores(Job._value2member_map_.get(job),list(range(memcached_core,4)))
    print("change cores of job: ",job)

def pause_jobs(job, previousCore):
    container = client.containers.get(job)
    container.reload()
    print("find pause job: ",job," - ",container.attrs['State']['Status'])
    updateJobStatus()
    # if(container.attrs['State']['Status'] == "exited"):
    #     print("in pause exited: ",job)
    #     jobList[job] = JobStatus.RECORDED.value
                
    #     logger.job_end(Job._value2member_map_.get(job))
    #     print(job," end!")
        
    if(jobList[job]==JobStatus.RUNNING.value):
        container.pause()
        
        logger.job_pause(Job._value2member_map_.get(job))
        previous_job_cores[job] = previousCore
        print(job," - previous core, ",previous_job_cores[job])
        print("pause job: ",job)


def updateJobStatus():
    for job, status in jobList.items():
        if (status == JobStatus.RUNNING.value) or (status==JobStatus.PAUSED.value):
            container = client.containers.get(job)
            container.reload()

            if(container.attrs['State']['Status'] == "exited"):
                print("in update exited: ",job)
                jobList[job] = JobStatus.EXITED.value
            elif(container.attrs['State']['Status'] == "paused"):
                print("in update paused: ",job)
                jobList[job] = JobStatus.PAUSED.value
            elif(container.attrs['State']['Status'] == "running"):
                print("in update running: ",job)
                jobList[job] = JobStatus.RUNNING.value

        if(jobList[job]==JobStatus.EXITED.value):
            jobList[job] = JobStatus.RECORDED.value     
            logger.job_end(Job._value2member_map_.get(job))
            print(job," end!")


def main_logic(running_jobs, usedList, previous_cores,setCore):
    global memcached_core
    if(previous_cores!=setCore):
        memcached_core = setCore
        os.system(f'pgrep memcached|xargs -n 1 sudo taskset -a -cp 0-{memcached_core-1}')
        logger.update_cores(Job.MEMCACHED,list(range(0,memcached_core)))

    for job in usedList:
        if (jobList[job] == JobStatus.PAUSED.value):
            if(len(running_jobs)!=0):
                pause_jobs(running_jobs[0],4-previous_cores)
            #unpause
            unpause_jobs(job)
            break

        if(jobList[job] == JobStatus.RUNNING.value):
            if(previous_cores!=setCore):
                change_cores(job)
            break

        if(jobList[job]==JobStatus.WAITING.value):
            # pause current running job
            if(len(running_jobs)!=0):
                pause_jobs(running_jobs[0],4-previous_cores)
            run_job(job)
            break


def launchJobs():
    
    countNum = 0

    while(True):
        print("==================================================== ",countNum+1)
        updateJobStatus()
        print("current job status: ",jobList)

        previous_cores = memcached_core
        memcachedState = monitorMemcached()

        running_jobs = [job for job, status in jobList.items() if status == JobStatus.RUNNING.value]
        paused_jobs = [job for job, status in jobList.items() if status == JobStatus.PAUSED.value]
        succeed_jobs = [job for job, status in jobList.items() if status == JobStatus.RECORDED.value]

        print("running jobs: ",running_jobs)
        print("paused jobs: ",paused_jobs)
        print("succeed jobs: ",succeed_jobs)

        if(len(running_jobs)==0) and (len(succeed_jobs)==7):
            break;

        if memcachedState == -1:
            main_logic(running_jobs,list(jobList.keys()),previous_cores, 1)

        elif memcachedState == 1:
            main_logic(running_jobs,jobList_2cores,previous_cores, 2)

        elif memcachedState == 0:
            if set([AllJob.BLACKSCHOLES.value, AllJob.CANNEAL.value, AllJob.VIPS.value, AllJob.RADIX.value, AllJob.DEDUP.value]).issubset(set(succeed_jobs)):
                main_logic(running_jobs,[AllJob.FERRET.value,AllJob.FREQMINE.value],previous_cores, 2)

            else:
                main_logic(running_jobs,[AllJob.BLACKSCHOLES.value, AllJob.CANNEAL.value, AllJob.VIPS.value, AllJob.RADIX.value, AllJob.DEDUP.value],previous_cores, 1)

        print("cores used by jobs: ", 4-memcached_core)

        if(len(succeed_jobs)==7):
            break;

        countNum = countNum+1
        time.sleep(2)


if __name__ == '__main__':
    logger.job_start(Job.MEMCACHED,[0],2)
    launchJobs()
    logger.job_end(Job.SCHEDULER)
