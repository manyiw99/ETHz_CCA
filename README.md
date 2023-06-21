# Cloud Computing Architecture(23Spring)
Summary of [23Spring ETHz Cloud Computing Architecture course](https://systems.ethz.ch/education/courses/2023-spring/cloud-computing-architecture.html)

## Introduction of Cloud Computing
### 1. What's cloud computing?
Cloud computing is the delivery of compute and storage resources on-demand, to offer:
- High performance
- Cost efficiency (economies of scale)
- Flexibility, elasticity
- High availability

### 2. Two types of cloud:
- Private clouds: limited to a single organization, e.g., enterprises have their own cloud facilities
- Public clouds: can be used by multiple organizations, e.g., public cloud providers like Amazon Web Services, Microsoft Azure, and Google Cloud rent hardware/software services on demand to the public

### 3. Evolution of cloud computing
- Cloud 1.0: Virtualization: Enable multiple users to share hardware
- Cloud 2.0: Hardware on demand: Rent virtual machines by the hour (or second) from public cloud provider
- Cloud 3.0: “Serverless computing”: Cloud provides an abstraction of compute and storage services, not servers

## Structure of the course
![image](https://github.com/manyiw99/ETHz_CCA/blob/main/Cloud%20Computing%20Architecture.png)

## Scripts
- `runPart3`: Automate job launching (Launch 7 jobs on 3 VMs, arrange the order and concurrency of jobs)
- `runPart4.py`: Monitor CPU untilization in real-time and dynamically start/pause/unpause jobs

## Reading Material
### Books
- The Datacenter as a Computer: Designing Warehouse-scale Machines(3rd edition), by Luiz Barroso, Urs Hölzle, Parthasarathy Ranganathan
- Computer Architecture: A Quantitative Approach(6th edition), Chapter 6: The Warehouse-Scale computer, by John Hennessy & David Patterson

### Papers
[1] Accelerators: [The Decline of Computers as a General Purpose Technology](https://cacm.acm.org/magazines/2021/3/250710-the-decline-of-computers-as-a-general-purpose-technology/fulltext)

[2] Accelerator Example: [Brainwave NPU: A Configurable Cloud-Scale DNN Processor for Real-Time AI](https://www.microsoft.com/en-us/research/uploads/prod/2018/06/ISCA18-Brainwave-CameraReady.pdf)

[3] Accelerator Example: [Video Coding Unit (VCU): Warehouse-Scale Video Acceleration: Co-design and Deployment in the Wild](https://research.google/pubs/pub50300/)

[4] Performance analysis: [Always Measure One Level Deeper](https://dl.acm.org/doi/pdf/10.1145/3213770)

[5] Virtualization: Bolt

[6] Container: gVisor

[7] microVM: firecracker

[8] Serverless: The rise of serverless computing, By Paul Castro

[9] Serverless: What serverless computing is and should become:the next phase of cloud computing

[10] Serverless: serverless in the wild 

[11] Cluster resource manager: Mesos

[12] Cluster resource manager: Borg

[13] Cluster resource manager: YARN

[14] Cluster resource manager: Omega

[15] Cluster resource manager: Sparrow

[16] Cluster resource manager: Quasar

