import os
import requests
import json
from datetime import datetime, timedelta
import argparse

OUTPUT_PATH                 = r"output"
DEAFULT_PROGRAMS_TO_DOWNLOAD= 10
URL                         = "https://eco99fm.maariv.co.il/api/v1/public/programs?page=1&itemsPerPage=%d&category_id=8"
TIME_FORMAT                 = "%Y-%m-%dT%H:%M:%S.%fZ"
DEFAULT_HOUR                = 21

def get_programs(start_date=None, items_count=DEAFULT_PROGRAMS_TO_DOWNLOAD):
    url = URL % items_count
    if start_date:
        prev_day = start_date - timedelta(days=1)
        url += "&date_filter=" + prev_day.strftime(TIME_FORMAT)

    response = requests.get(url)
    if response.status_code <= 200 and response.status_code <300:
        return json.loads(response.content)["programs"]

    return None

def sort_programs_by_date(programs, asc=True):
    return sorted(programs, key=lambda s: datetime.strptime(s["insert_date"], TIME_FORMAT), reverse=not asc)

def create_file_name_from_program(program):
    if not program:
        return None

    name = program["download_file_name"]
    if not name:
        return None

    return name.replace("haboker_full_", "")

def download_program(program_data, output_path):
    print("[+] Starting to download %s" % program_data["download_url"])
    program_request = requests.get(program_data["download_url"])

    if program_request.status_code >= 200 and program_request.status_code < 300:
        print ("[+] Finished download")
        print("[+] Writing to path %s" % output_path)

        with open(output_path, "wb") as f:
            f.write(program_request.content)
        print("[+] Wrote to file")
        return True
    return False

# def download_last_programs():
#     if not os.path.isdir(OUTPUT_PATH):
#         print("[+] Creating %s" % OUTPUT_PATH)
#         os.mkdir(OUTPUT_PATH)
#
#     programs = sort_programs_by_date(get_programs(DEAFULT_PROGRAMS_TO_DOWNLOAD))
#
#     for program in programs:
#         result_path = os.path.join(OUTPUT_PATH, program["download_file_name"])
#         if os.path.exists(result_path):
#             print("[*] %s exists. continuing..." % result_path)
#             continue

def main():
    today = datetime.today()
    parser = argparse.ArgumentParser("Tal and Aviad downloader")
    parser.add_argument("--month", "-m", type=int, default=today.month)
    parser.add_argument("--year", "-y", type=int, default=today.year)
    parser.add_argument("--count", "-c", type=int, default=DEAFULT_PROGRAMS_TO_DOWNLOAD)
    args = parser.parse_args()

    dt_from_user = datetime(year=args.year, month=args.month, day=1, hour=DEFAULT_HOUR)

    programs = sort_programs_by_date(get_programs(dt_from_user, args.count))

    for program in programs:
        download_program(program, os.path.join(OUTPUT_PATH, create_file_name_from_program(program)))

if __name__ == '__main__':
    main()