from bs4 import BeautifulSoup
import requests, time, sys, queue, threading

runDelay = 30

while True:
    filtered_out_skills = []
    print("RUNNING...")
    
    while True:
        print("Filter out skills you're unfamiliar with:                TYPE 'ok' TO continue or 'q' to quit.")
        unfamiliar_skill = input('  >').strip().lower()
        if unfamiliar_skill == 'q':
            sys.exit()
        if unfamiliar_skill != "" and not unfamiliar_skill.isspace() and unfamiliar_skill != "ok":
            filtered_out_skills.append(unfamiliar_skill)
        elif unfamiliar_skill == "ok":
            print("CONTINUING SUCCESSFULLY...")
            break
        else:
            print("Invalid input. Please enter a skill or type 'ok' to continue.")

    print(f'Filtering out \"{filtered_out_skills}\"...')
    
    def find_jobs(lock, stop_flag):
        numberOfTimesRan = 0
        found_job = False
        while not stop_flag.is_set():
            try:
                html_text = requests.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=python&txtLocation=').text
                soup = BeautifulSoup(html_text, 'lxml')
                jobs = soup.find_all('li', class_ = 'clearfix job-bx wht-shd-bx')
                with lock:
                    for job in jobs:
                        published_date = job.find('span', class_='sim-posted').span.text.strip()
                        if 'few' in published_date:
                            company_name = job.find('h3', class_='joblist-comp-name').text.replace(' ', "")
                            skills = job.find('span', class_ = "srp-skills").text.lower().replace(' ', "")
                            more_info = job.header.h2.a['href']
                            if all(skill not in skills for skill in filtered_out_skills):
                                print(f'Company name: {company_name.strip()}')
                                print(f'Required skills: {skills.strip()}')
                                print(f"More info: {more_info.strip()}")
                                print('')
                                found_job=True
                    numberOfTimesRan += 1

                    if not found_job:
                        print("No jobs with current filters found")
                    print(f"Script runs every {runDelay} seconds.       ENTER 'q' TO STOP, and 'e' TO EDIT       ran {numberOfTimesRan} times.")

            except Exception as e:
                print(f"Error in find_jobs(): {e}")
            time.sleep(runDelay)  # wait for specified delay

    def read_input(stop_flag):
        global runDelay
        while not stop_flag.is_set():
            line = input()
            if line.lower() == 'q':
                print('Exiting program...                   (This may take a few seconds)')
                stop_flag.set()
                break
            elif line.lower() == 'e':
                try:
                    newDelay = int(input("Enter new delay (in seconds): "))
                    if newDelay > 0:
                        runDelay = newDelay
                        print(f"Delay set to {runDelay} seconds")
                    else:
                        print("Delay must be a positive integer")
                except ValueError:
                    print("Invalid input. Please enter a positive integer")

    lock = threading.Lock()
    stop_flag = threading.Event()
    jobs_thread = threading.Thread(target=find_jobs, args=(lock, stop_flag))

    while not stop_flag.is_set():
        jobs_thread.start()

        quit_queue = queue.Queue()
        quit_thread = threading.Thread(target=read_input, args=(stop_flag,))
        quit_thread.start()

        while jobs_thread.is_alive():
            time.sleep(runDelay)  # wait for specified delay

        quit_thread.join()
        jobs_thread.join()

        print("Exited successfully")
        while True:
            answer = input("Do you want to run the script again? (y/n) ").lower()
            if answer == 'n':
                sys.exit()
            elif answer == 'y':
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

        if answer != 'y':
            break