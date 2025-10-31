#News scraper that scapes latest news on a website and summarizes the articles
import requests
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

headers = {"User-Agent": "Mozilla/5.0"}

sentences_to_remove = ["Oops, something went wrong", "Sign in to access your portfolio", "Something went wrong", "Read more here"]

#scrapes news articles and returns a list of objects
def scrape_news():
    url = "https://finance.yahoo.com/topic/latest-news/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    news_links = set()
    for a in soup.find_all(attrs={"title": True}): #only prints out ones with titles which will be all the news articles
        href = a.get("href")
        if (str(href).startswith("http")):
            news_links.add(href)
    final_object = []
    for article in news_links:
        response = requests.get(article, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        title_object = soup.find("h1", class_ = "cover-title")
        title = ""
        if title_object != None:
            title = title_object.text
        text_for_article = ""
        for a in soup.find_all("p"):
            text = str(a.text)
            for word in sentences_to_remove:
                text = str(text).replace(word, "")
            
            text_for_article += text
        if text_for_article != "":
            final_object.append({
                "link": article,
                "title": title,
                "text" : text_for_article
            })
    return final_object

#passes list of news objects and returns text through llm
def summarize_articles(articles):
    """Summarize each article using OpenAI"""
    load_dotenv()  # Loads environment variables from .env

    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    summarized = []

    for article in articles:
        try:
            prompt = f"Summarize this article in 50 words or less:\n\n{article['text']}"
            response = model.invoke(prompt)

            summary = response.content if hasattr(response, "content") else str(response)
            article["summary"] = summary
            summarized.append(article)

            print(f"Link: {article['link']}")
            print(f"Summarized: {article['title']}")
            print(summary)
            print("----------------------------------------------------")
            print("")

        except Exception as e:
            print(f" Error summarizing {article['title']}: {e}")

    return summarized

def main():
    articles = scrape_news()
    summarize_articles(articles)

if __name__ == "__main__":
    main()
