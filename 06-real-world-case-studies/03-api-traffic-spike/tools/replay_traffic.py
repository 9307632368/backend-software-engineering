"""Replay a LOCAL synthetic request trace and print actual response counts."""
from collections import Counter
import csv
import os
import time
from pathlib import Path
import httpx


def replay(csv_path:Path,base_url:str,delay:bool=False):
    totals=Counter()
    start=time.monotonic()
    with httpx.Client(timeout=5) as client, csv_path.open(newline="",encoding="utf-8") as source:
        for entry in csv.DictReader(source):
            if delay:
                target=int(entry["at_milliseconds"])/1000
                remaining=target-(time.monotonic()-start)
                if remaining>0:time.sleep(remaining)
            response=client.get(base_url.rstrip("/")+"/work",headers={"X-Client-Key":entry["client_key"]})
            totals[response.status_code]+=1
            print(f'{entry["at_milliseconds"]:>5}ms  {entry["client_key"]:<12} {response.status_code}')
    print("Response counts for this run:",dict(sorted(totals.items())))
    return totals


if __name__=="__main__":
    root=Path(__file__).resolve().parents[1]
    replay(root/"data"/"synthetic-requests.csv",
           os.getenv("BASE_URL","http://127.0.0.1:8000"),
           delay=os.getenv("REAL_TIME_REPLAY","0")=="1")
