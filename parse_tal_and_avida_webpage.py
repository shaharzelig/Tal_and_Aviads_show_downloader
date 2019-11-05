import os
import time

import requests
import json
from datetime import datetime

OUTPUT_PATH                 = r"d:\tal_and_avida_shows"
MAX_PROGRAMS_TO_DOWNLOAD    = 10
URL                         = "https://eco99fm.maariv.co.il/api/v1/public/programs?page=1&itemsPerPage=%d&category_id=8"
TIME_FORMAT                 = "%Y-%m-%dT%H:%M:%S.%fZ"



def get_show_data_by_date(date):
    pass


def get_programs(programs_count):
    response = requests.get(URL % programs_count)
    if response.status_code <= 200 and response.status_code <300:
        return json.loads(response.content)["programs"]

    return None

def sort_programs_by_date(programs):
    return sorted(programs, key=lambda s: datetime.strptime(s["insert_date"], TIME_FORMAT), reverse=True)

def download_program(program_data, output_path):
    print "[+] Starting to download %s" % program_data["download_url"]
    program_request = requests.get(program_data["download_url"])

    if program_request.status_code >= 200 and program_request.status_code < 300:
        print "[+] Finished download"
        print "[+] Writing to path %s" % output_path

        with open(output_path, "wb") as f:
            f.write(program_request.content)
        print "[+] Wrote to file"
        return True
    return False

def download_last_programs():
    if not os.path.isdir(OUTPUT_PATH):
        print "[+] Creating %s" % OUTPUT_PATH
        os.mkdir(OUTPUT_PATH)

    programs = sort_programs_by_date(get_programs(MAX_PROGRAMS_TO_DOWNLOAD))

    for program in programs:
        result_path =os.path.join(OUTPUT_PATH, program["download_file_name"])
        if os.path.exists(result_path):
            print "[*] %s exists. continuing..." % result_path
            continue

def is_date_today(date_to_check):
    programs_date = datetime.strptime(date_to_check, TIME_FORMAT)
    if programs_date.date() == datetime.today().date():
        return True
    return False

def get_todays_show():
    programs = sort_programs_by_date(get_programs(MAX_PROGRAMS_TO_DOWNLOAD))
    for program in programs:
        if is_date_today(program["insert_date"]):
            return program

    return None

def main():
    print "trying to download todays_show"
    program = get_todays_show()
    while not program:
        time.sleep(10)
        program = get_todays_show()

    output_file_path = os.path.join(OUTPUT_PATH, program["download_file_name"])
    if os.path.exists(output_file_path):
        print "[*] File %s already exists" % output_file_path
        return True
    if download_program(program, output_file_path):
        return True

    return False

if __name__ == '__main__':
    main()