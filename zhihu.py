'''
This code can download and save "class representative" post, 
"article-only" post and "bunch of pictures" post.

Read the link directly from the clipboard, then double-click the bat file to run it.

BAT FILE:
@py.exe "D:\Rilla\zhihu.py" %*
@pause

Instruction:
go to the post on zhihu.com, click "share", then double click the bat file, choose the category of post.

10/23/2022
'''

import os
import requests
import time
from bs4 import BeautifulSoup
from threading import Thread
from tkinter import Tk


SAVE_DIRECTORY = r"D:\Rilla\zhihu"

HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
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
    validname = validname.replace('\t', '')
    validname = validname.replace('\r', '')
    validname = validname.replace('\n', '')
    validname = validname.replace('\xa0', '')
    validname = validname.replace('\u200b', '')
    validname = validname.replace('？', '').strip()
    return validname


def rillaget(url, dir_name, header):
    filename = url.split('/')[-1]
    filename = make_name_valid(filename)
    total_path = os.path.join(dir_name, filename)

    try:
        response = requests.get(url, headers=header, timeout=50)

        if response.status_code == requests.codes.ok:  # ok means 200 only
            with open(total_path, 'wb') as f:
                f.write(response.content)
            print(f"{filename}  Download successful")
        else:
            print(f"{url} Download Failed | Status Code： {response.status_code}")

    except requests.exceptions.ConnectionError:
        print(f"{url} \t Unable to load\n")

    except Exception as e:
        print(f"{url} Abnormalities occur：\n{e}")


def find_title_of_the_main_post(soup):
    return soup.title.get_text().replace(' - 知乎', '').strip()


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
        image_url = image_raw.split('?')[0]
        downlist.append(image_url)

    # Sometimes the original post picture resolution is too low
    # Will cause no original picture of the situation, generally will be _720w suffix
    if len(div_img_origin_image) == 0:
        div_img_content_image_lazy = soup.find_all(
            'img', class_='content_image lazy')
        for element in div_img_content_image_lazy:
            image_raw = element.get('data-actualsrc')
            image_url = image_raw.split('?')[0].replace('_720w', '')
            downlist.append(image_url)
    return downlist


def find_author(soup):
    div_AuthorInfo = soup.find('span', class_="UserLink AuthorInfo-name")
    post_author = div_AuthorInfo.get_text().strip()
    post_author = make_name_valid(post_author)
    return post_author


def rilla_downloader(downlist, PATH):
    threads = []
    for image_url in downlist:
        thread = Thread(target=rillaget, args=[
                        image_url, PATH, HEADER])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def solo_images():
    os.chdir(SAVE_DIRECTORY)
    soup = get_soup_from_webpage(QUESTION_URL, HEADER, 25)
    title = find_title_of_the_main_post(soup)
    author = find_author(soup)
    downlist = extract_images_from_post(soup)
    print(f"{title} \nAuthor {author} \nFound {len(downlist)} of images")
    rilla_downloader(downlist, SAVE_DIRECTORY)
    print(f"Save to {SAVE_DIRECTORY}")


def main():
    print(f"Now accessing：\n{QUESTION_URL}")
    description = "Hello, what you wanna do today? \nA.Get links to all the images \
    in the class rep post\nB.Save article\nC.Save all the pictures of the post with all the pictures\n>"
    selection = str(input(description)).upper()
    if selection == 'A':
        class_president()
    elif selection == "B":
        save_text()
    elif selection == "C":
        solo_images()
    else:
        print("Your Majesty's instructions are unclear, please forgive my \
        humble servant and try again later.")


def class_president():
    os.chdir(SAVE_DIRECTORY)
    # Get all the links in the class rep post
    main_post_soup = get_soup_from_webpage(QUESTION_URL, HEADER, 25)
    print(QUESTION_URL)  # Print this posting address
    # Print the title of this post
    print(find_title_of_the_main_post(main_post_soup))
    print("\n", "~~"*70, "\n")  # Print dividers
    questions_links = collect_cards_inside_question(main_post_soup)
    print(f"Found{len(questions_links)}links, now are opening them")

    # If it does find the link, create a new folder and prepare to start downloading
    if not len(questions_links):
        return
    else:
        mainfolder = " ".join([QUESTION_URL.split(
            '/')[-1], find_title_of_the_main_post(main_post_soup)])
        mainfolder = make_name_valid(mainfolder)
        if not os.path.exists(mainfolder):
            os.makedirs(mainfolder)

    # Get the address of the original image in each link in turn
    for each_individual_question in questions_links:
        particular_question_soup = get_soup_from_webpage(
            each_individual_question, HEADER, 25)

        # Need to determine whether there is a picture first, sometimes the post has been
        # deleted, then return empty results
        downlist = extract_images_from_post(particular_question_soup)
        if not downlist:
            print("Pictures not found, may have been harmonized")
            continue

        dirname = find_author(particular_question_soup)
        print(
            f"\nBeing opened {each_individual_question}\nThe author of the post is {dirname}\n")

        # Download the acquired images and save them in the folder of the author id of the post,
        # for subsequent organization
        author_folder = os.path.join(mainfolder, dirname)
        if not os.path.exists(author_folder):
            os.makedirs(author_folder)

        # Perform multi-threaded downloads
        rilla_downloader(downlist, author_folder)

        # Wait a few seconds to give the server a break
        time.sleep(2)
    print(f"Saved the image to {SAVE_DIRECTORY}")


def save_text():
    os.chdir(SAVE_DIRECTORY)
    soup = get_soup_from_webpage(QUESTION_URL, HEADER, 25)
    para_title = make_name_valid(find_title_of_the_main_post(soup))
    para_author = make_name_valid(find_author(soup))
    text_name = "".join([para_title, ' _ ', para_author, '.txt'])
    article = soup.find("span", attrs={
        "itemprop":"text",
        "options":"[object Object]"
        })
    for br in article.find_all("br"):
        br.replace_with("\n")
    print(text_name)

    with open(text_name, 'wt', encoding='utf-8') as f:
        for each_line in article:
            if each_line.text == '':
                continue
            elif each_line.name == 'p':
                f.write(each_line.text.strip() + '\n')
            elif each_line.name == 'blockquote':
                f.write('\n' + each_line.text.strip() + '\n\n')
        f.write('\n' + CLIPBOARD)
    print(f"Saved the article to {SAVE_DIRECTORY}")


def get_Clipboard_Text():
    root = Tk()
    root.withdraw()  # keep the window from showing
    return root.clipboard_get()


if __name__ == '__main__':

    # This code creates a blank widget to get the clipboard content from OS.
    CLIPBOARD = get_Clipboard_Text()

    if "zhihu.com/question" in CLIPBOARD and '\n' in CLIPBOARD:
        split = CLIPBOARD.split('\n')
        q_title, QUESTION_URL = split[0], split[1]

        main()

        print("～～花びらをまく～～")

    else:
        print(CLIPBOARD)
        print("Please double check the clipboard content to make sure this is a Zhihu share link")
