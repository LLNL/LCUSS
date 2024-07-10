#!/usr/bin/env -S flux python

###############################################################################
#
#  jobinfo.py -- Print checkjob-type info for the given slurm or flux jobid
#                (running or completed)
#
#  Author: Jeff Long & Jane Herriman
###############################################################################

import argparse
from datetime import datetime
import flux
import flux.job
import json
import os
import re
import subprocess
import sys

def parse_slurm_output(cmd_string):
    os.environ['SLURM_TIME_FORMAT'] = '%a %m/%d %H:%M:%S'
    jobinfo = (
        subprocess.check_output(cmd_string, shell=True)
        .decode("utf-8")
        .splitlines()
    )
    header_str = jobinfo[0]
    info_str    = jobinfo[1]
    headers = header_str.split(',')
    info    = info_str.split(',')
    return headers, info

def get_sacct_jobinfo(jobid):
    """Print job info from `sacct` for given slurm jobid (pending, running or completed)"""

    cmd_string = f'sacct -j {jobid} --parsable2 --delimiter , -X -o JobID,JobName,State,User,Group,Account,Partition,QOS,Timelimit,Submit,Eligible,Start,End,Elapsed,Priority,NNodes,NCPUS,MinCPUNode,NodeList,WorkDir,SubmitLine'

    try:
        headers, info = parse_slurm_output(cmd_string)

        for index, item in enumerate(headers):
            print(f'{item:11}  :  {info[index]}')

        jobstate = info[2]

        return jobstate

    except Exception as e:
        print(
            f"[ERROR] - unable to get info for jobid: {jobid}",
            file=sys.stderr,
        )

def get_squeue_jobinfo(jobid, jobstate):
    """ Print select job info from `squeue` for given slurm jobid & jobstate (pending, running or completed)"""

    if jobstate == "PENDING":

        try:
            cmd_string = f'squeue -j {jobid} --start -o "%E,%S,%R"'
            headers, info = parse_slurm_output(cmd_string)

            print(f'{"Dependency":11}  :  {info[0]}')
            print(f'{"EstStart":11}  :  {info[1]}')
            print(f'{"Reason":11}  :  {info[2]}')

        except Exception as e:
            print(
                f"[ERROR] - unable to get estimated start info for jobid: {jobid}",
                file=sys.stderr,
            )


def parse_time(time):
    """
    turn a bunch of seconds into something human readable
    """
    # Function re-used from Ryan Day's
    # /usr/global/tools/flux_wrappers/bin/squeue
    time = int(time)

    # Convert time into hours, minutes, and seconds.
    days = time // 86400
    hours = time // 3600 % 24
    minutes = time // 60 % 60
    seconds = time % 60

    if days > 0:
      return f"{days}-{hours}:{minutes:02}:{seconds:02}"

    if hours > 0:
        return f"{hours}:{minutes:02}:{seconds:02}"

    return f"{minutes:02}:{seconds:02}"

def parse_timestamp(time):
    date = datetime.fromtimestamp(time)
    date_str = date.strftime("%a %m/%d/%Y %H:%M:%S")

    # if the job hasn't started yet, a date in either
    # 1969 or 1970 is returned
    year = int(date.strftime("%Y"))
    if year < 2023:
        return "Unknown"

    return date_str

def report_urgency(urgency):
    if urgency <= 16:
        if urgency == 0:
            return "Hold"
        elif urgency == 16:
            return "Default"
        else:
            return "Low"
    elif urgency > 16:
        if urgency == 31:
            return "Expedited"
        elif urgency < 31:
            return "Elevated"

def get_flux_job_info(jobid):
    # Start flux connection & create flux handle
    handle = flux.Flux()

    jobid_int = flux.job.JobID(jobid)
    payload = {"id": jobid_int, "attrs": ["all"]}
    rpc = flux.job.list.JobListIdRPC(handle, "job-list.list-id", payload)
    jobinfo = rpc.get_jobinfo()

    try:
        payload = {"id": jobid_int, "keys": ["jobspec"], "flags": 0}
        jobspec = json.loads(handle.rpc("job-info.lookup", payload).get()["jobspec"])
    except PermissionError as e:
        print("You can only look up this info for your own Flux jobs!")
        sys.exit(1)


    # Try to mimic slurm output:
    print(f'{"JobID":11}  :  {jobinfo.id.f58}')
    print(f'{"JobName":11}  :  {jobinfo.name}')
    print(f'{"State":11}  :  {jobinfo.state}')
    print(f'{"User":11}  :  {jobinfo.username}')
    #print(f'{"Account":11}  :  {job.}')
    print(f'{"Partition":11}  :  {jobinfo.queue}')
    #print(f'{"QOS":11}  :  {job.}')
    print(f'{"Timelimit":11}  :  {parse_time(jobinfo.duration)}')
    print(f'{"Submit":11}  :  {parse_timestamp(jobinfo.t_submit)}')
    print(f'{"Elapsed":11}  :  {parse_time(jobinfo.runtime)}')
    print(f'{"Urgency":11}  :  {report_urgency(jobinfo.urgency)}')
    print(f'{"Start":11}  :  {parse_timestamp(jobinfo.t_run)}')
    print(f'{"End":11}  :  {parse_timestamp(jobinfo.expiration)}')
    print(f'{"NNodes":11}  :  {jobinfo.nnodes}')
    print(f'{"NCores":11}  :  {jobinfo.ncores}')
    print(f'{"NTasks":11}  :  {jobinfo.ntasks}')
    print(f'{"NodeList":11}  :  {jobinfo.nodelist}')
    print(f'{"WorkDir":11}  :  {jobspec["attributes"]["system"]["cwd"]}')
    print(f'{"SubmitLine":11}  :  {" ".join(jobspec["tasks"][0]["command"])}')
    print(f'{"Dependency":11}  :  {jobinfo.dependencies}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get information about slurm or flux job")
    parser.add_argument(
        "--jobid",
        "-j",
        required=True,
        help="Slurm or Flux job id. Required field."
    )
    args = parser.parse_args()

    if bool(re.fullmatch("[0-9]+_?[0-9]*", args.jobid)):
        state = get_sacct_jobinfo(args.jobid)
        get_squeue_jobinfo(args.jobid, state)
    elif bool(re.fullmatch("f\w*", args.jobid)):
        get_flux_job_info(args.jobid)
    else:
        print('Invalid Slurm or Flux ID. Either an integer (Slurm) or an alphanumeric string starting with "f" (Flux) is required.')
        sys.exit(1)

    sys.exit(0)
