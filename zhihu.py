import os
import requests
import time
from bs4 import BeautifulSoup
from threading import Thread

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
}


def get_soup_from_webpage(url, header, timeout=None):
    response = requests.get(url, headers=header, timeout=timeout)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')

    # Discard junk elements in web pages for faster processing
    for script in soup.find_all("script"):
        script.decompose()
    for style in soup.find_all("style"):
        style.decompose()

    return soup


def make_name_valid(validname):
    validname = validname.replace('\\', '_')
    validname = validname.replace('/', '_')
    validname = validname.replace(':', '_')
    validname = validname.replace('*', '_')
    validname = validname.replace('?', '_')
    validname = validname.replace('"', '_')
    validname = validname.replace('<', '_')
    validname = validname.replace('>', '_')
    validname = validname.replace('|', '_')
    validname = validname.replace('\t', '_')
    validname = validname.replace('\r', '_')
    validname = validname.replace('\n', '_')
    validname = validname.replace('\xa0', '_')
    validname = validname.replace("\u200b", "_")
    validname = validname.strip()
    return validname


def rillaget(url, dir_name, header):
    filename = url.split("/")[-1]
    filename = make_name_valid(filename)
    total_path = os.path.join(dir_name, filename)

    try:
        response = requests.get(url, headers=header, timeout=50)

        if response.status_code == requests.codes.ok:  # ok means 200 only
            with open(total_path, 'wb') as fd:
                for chunk in response.iter_content(1024):
                    fd.write(chunk)
            print(f"{filename}  Download Successful")
        else:
            print(f"{url} Download Failed Status Code： {response.status_code}")

    except requests.exceptions.ConnectionError:
        print(f"{url} \t Unable to load\n")

    except Exception as e:
        print(f"{url} Abnormalities occur：\n{e}")


def get_soup_from_localhtml(webpage):
    soup = BeautifulSoup(open(webpage, encoding='utf-8'), features='lxml')
    return soup


def find_title_of_the_main_post(soup):
    return soup.title.get_text()


def collect_cards_inside_question(soup):
    questions_links = []
    div_a_LinkCard = soup.find_all('a', class_="LinkCard new")
    for each_card in div_a_LinkCard:
        hyperlink_LinkCard = each_card.get('href')
        questions_links.append(hyperlink_LinkCard)
    return questions_links


def extract_images_from_post(soup):
    downlist = []
    div_img_origin_image = soup.find_all('img', class_="origin_image")
    for element in div_img_origin_image:
        image_raw = element.get('data-original')
        image_url = image_raw.split("?")[0]
        downlist.append(image_url)
    return downlist


def find_author(soup):
    div_AuthorInfo = soup.find('span', class_="UserLink AuthorInfo-name")
    post_author = div_AuthorInfo.get_text().strip()
    post_author = make_name_valid(post_author)
    return post_author


def user_input_module():
    customer_input = 'R'
    while customer_input == 'R':
        question = str(input("\nPlease input question number, that is the first number on your url\nSample: https://www.zhihu.com/question/60836727/answer/2411871331\n60836727 is the question number\n"))
        answer = str(input(
            "\nPlease input answer number, that is the second number on your url\nIn the sample above, 2411871331 is the answer number\n"))
        QUESTION = "".join(
            ["https://www.zhihu.com/question/", question, "/answer/", answer])
        customer_input = str(input(
            f"\nThe url you input is {QUESTION}, is that correct? if yes, press ANY key, otherwise, press R to re-enter.\n")).capitalize()
    return QUESTION


def main():
    QUESTION = user_input_module()

    # Get all the links in the class rep post
    main_post_soup = get_soup_from_webpage(QUESTION, HEADER, 25)
    print(QUESTION)  # Print this posting address
    # Print the title of this post
    print(find_title_of_the_main_post(main_post_soup))
    print("\n", "~~"*70, "\n")  # Print dividers
    questions_links = collect_cards_inside_question(main_post_soup)
    print(f"Find the {len(questions_links)} links and open them in order")

    # If you do find the link, create a new folder and prepare to start downloading
    if not len(questions_links):
        return
    else:
        mainfolder = " ".join([QUESTION.split(
            '/')[-1], find_title_of_the_main_post(main_post_soup).replace(" - 知乎", "")])
        mainfolder = make_name_valid(mainfolder).replace("？", "").strip()
        if not os.path.exists(mainfolder):
            os.makedirs(mainfolder)

    # Get the address of the original image in each link in turn
    for each_individual_question in questions_links:
        particular_question_soup = get_soup_from_webpage(
            each_individual_question, HEADER, 25)
        dirname = find_author(particular_question_soup)
        # Print this posting address
        print(
            f"\nis opening {each_individual_question}\n the post by {dirname}\n")
        downlist = extract_images_from_post(particular_question_soup)

        # Download the acquired images and save them in the folder of the author id of the post, for subsequent organization
        author_folder = os.path.join(mainfolder, dirname)
        if not os.path.exists(author_folder):
            os.makedirs(author_folder)

        # Perform multi-threaded downloads
        threads = []
        for image_url in downlist:
            thread = Thread(target=rillaget, args=[
                            image_url, author_folder, HEADER])
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

        # Wait a few seconds to give the server a break
        time.sleep(2)


if __name__ == '__main__':
    main()
    # A general expression, something exciting or "I'm coming" appears.
    print("ｷﾀﾜァ*･゜ﾟ･*:.｡..｡.:*･゜(n‘∀‘)ηﾟ･*:.｡. .｡.:*･゜ﾟ･* !!!!!")
