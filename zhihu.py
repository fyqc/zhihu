'''
This code can download and save "Class Representative" posts and "Article Only" posts.
Please put the address of "Class Representative" post into CLASS_PRESIDENT
Put the address of the "article-only" post into ARTICLE_SHARE
and specify the path of the save folder for both of them.

4/9/2022
'''

import os
import requests
import time
from bs4 import BeautifulSoup
from threading import Thread


HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
}

# 王思聪为什么没能搞定孙一宁？ - 爱吃蛋挞的少女的回答 - 知乎
ARTICLE_SHARE = "https://www.zhihu.com/question/465217042/answer/1946460662"
ARTICLE_SHARE_PATH = r"C:\Users\Rilla\Desktop"

# 女上司好看是种怎样的体验？ - 阿喏呀的回答 - 知乎
CLASS_PRESIDENT = "https://www.zhihu.com/question/266626906/answer/2429500615"
CLASS_PRESIDENT_PATH = r"D:\zhihu question"


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
            with open(total_path, 'wb') as fd:
                for chunk in response.iter_content(1024):
                    fd.write(chunk)
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


def main():
    description = "哈啰，今天想要做什么呢？\nA.获取课代表帖中的所有图片\nB.保存文章\n>"
    selection = str(input(description)).upper()
    if selection == 'A':
        class_president()
    elif selection == "B":
        save_text()
    else:
        print("皇上指示不明，请恕臣妾愚钝。")


def class_president():
    os.chdir(CLASS_PRESIDENT_PATH)

    main_post_soup = get_soup_from_webpage(CLASS_PRESIDENT, HEADER, 25)
    print(CLASS_PRESIDENT)  
    print(find_title_of_the_main_post(main_post_soup))  
    print("\n", "~~"*70, "\n")  
    questions_links = collect_cards_inside_question(main_post_soup)
    print(f"Found the{len(questions_links)} segment")

    # If you do find the link, create a new folder and prepare to start downloading
    if not len(questions_links):
        return
    else:
        mainfolder = " ".join([CLASS_PRESIDENT.split(
            '/')[-1], find_title_of_the_main_post(main_post_soup)])
        mainfolder = make_name_valid(mainfolder)
        if not os.path.exists(mainfolder):
            os.makedirs(mainfolder)

    # Get the address of the original image in each link in turn
    for each_individual_question in questions_links:
        particular_question_soup = get_soup_from_webpage(
            each_individual_question, HEADER, 25)
        dirname = find_author(particular_question_soup)
        # Print this link post address
        print(f"\nNow opening {each_individual_question}\nThe author of this post is {dirname}\n")
        downlist = extract_images_from_post(particular_question_soup)

        # Download the acquired images and save them in the folder of the author id of the post
        # for subsequent organization
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


def save_text():
    os.chdir(ARTICLE_SHARE_PATH)
    soup = get_soup_from_webpage(ARTICLE_SHARE, HEADER, 25)
    para_title = find_title_of_the_main_post(soup)
    para_author = find_author(soup)
    text_name = "".join([para_title, ' _ ', para_author, '.txt'])
    texts = soup.find('div', class_="RichContent-inner")
    tag_p = texts.find_all('p')

    print(text_name)
    print(f"Found the {len(tag_p)} segment")
    share_info_line = "".join([para_title, ' - ', para_author, '的回答 - 知乎'])

    with open(text_name, 'wt', encoding='utf-8') as f:
        for each_para in tag_p:
            pure_para = each_para.text
            f.write(pure_para + '\n')
        f.write('\n' + share_info_line + '\n' + ARTICLE_SHARE)


if __name__ == '__main__':
    main()
    print("～～花びらをまく～～")
