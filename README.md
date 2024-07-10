# LCUSS: Livermore Computing User and System Scripts
## Overview
LCUSS is a collection of scripts used to improve productivity on HPC systems for both administrators and general users. These may include general scripts for user management, scripts for helping users interact with Livermore Computing (LC) resource management software (e.g. SLURM and Flux), and scripts to automate common user command-line tasks on LC and other HPC machines.

## Usage

For example, `jobinfo.py -j <JOBID>` produces output with the following format when querying Slurm and Flux jobs, respectively:

```
$ jobinfo.py -j 817256
JobID        :  817256
JobName      :  mysubmitscript.sh
State        :  RUNNING
User         :  janeh
Group        :  janeh
Account      :  lc
Partition    :  pbatch
QOS          :  normal
Timelimit    :  00:01:00
Submit       :  Wed 07/10 16:53:31
Eligible     :  Wed 07/10 16:53:31
Start        :  Wed 07/10 16:53:31
End          :  Unknown
Elapsed      :  00:00:09
Priority     :  110433
NNodes       :  2
NCPUS        :  72
MinCPUNode   :
NodeList     :  pascal[61-62]
WorkDir      :  /usr/WS1/janeh
SubmitLine   :  sbatch mysubmitscript.sh
```

```
$ jobinfo.py -j f3GRo7NrwZV9
JobID        :  f3GRo7NrwZV9
JobName      :  mysubmitscript.sh
State        :  RUN
User         :  janeh
Partition    :  pdebug
Timelimit    :  01:00
Submit       :  Wed 07/10/2024 16:50:55
Elapsed      :  00:15
Urgency      :  Default
Start        :  Wed 07/10/2024 16:50:55
End          :  Wed 07/10/2024 16:51:55
NNodes       :  2
NCores       :  128
NTasks       :  2
NodeList     :  tioga[22,25]
WorkDir      :  /usr/WS1/janeh
SubmitLine   :  flux broker {{tmpdir}}/script
Dependency   :
```


## Contributing
To contribute, please submit a pull request to the `main` branch.

## License
Released under the Apache 2.0 license w/ LLVM exception as `LLNL-CODE-866504`.
