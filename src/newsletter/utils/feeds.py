from django.conf import settings

from urllib.parse import urlparse
from google_alerts import GoogleAlerts

from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.chains.mapreduce import MapReduceChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

import html
import feedparser


class Feed:
    def __init__(self):
        self.email = settings.FEEDS_EMAIL
        self.password = settings.FEEDS_PASSWORD

    def create_feed(
        self,
        topic,
        delivery="RSS",
        match_type="BEST",
        alert_frequency="AS_IT_HAPPENS",
        region="US",
        language="en",
    ):
        """
        Args:
            delivery: 'RSS' or 'MAIL'
            match_type: 'ALL' or 'BEST'
            alert_frequency: 'AT_MOST_ONCE_A_DAY' or 'AS_IT_HAPPENS' or 'AT_MOST_ONCE_A_WEEK'
        """
        ga = GoogleAlerts(self.email, self.password)
        ga.authenticate()
        feed = ga.create(
            topic,
            {
                "delivery": delivery,
                "match_type": match_type,
                "alert_frequency": alert_frequency,
                "region": region,
                "language": language,
            },
        )
        return feed["rss_url"]

    def read_feeds(self, rss_url):
        results = []

        feed = feedparser.parse(rss_url)

        entries = feed.entries
        for entry in entries:
            new_entry = {}
            
            google_affiliate_url_parse = urlparse(entry.link).query.split("&")
            for url in google_affiliate_url_parse:
                if url.startswith("url"):
                    new_entry["link"] = url.split("=")[-1]
            
            new_entry["title"] = html.unescape(
                entry["title"].replace("</b>", "").replace("<b>", "")
            )
            new_entry["summary"] = html.unescape(
                entry["summary"].replace("</b>", "").replace("<b>", "")
            )
            results.append(new_entry)
        return results


# Map
map_template = """The following is a set of documents
{docs}
Based on this list of docs, please identify the main themes 
Helpful Answer:"""

# Reduce
reduce_template = """The following is set of summaries:
{doc_summaries}
Take these and distill it into a final, consolidated summary of the main themes. 
Helpful Answer:"""


def get_feeds_summary(feeds: list):
    documents = [Document(page_content=feed["summary"]) for feed in feeds]
    
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    
    # Map 
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)
    # Reduce
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)
    
    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="docs"
    )
    
    # Combines and iteravely reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        # This is final chain that is called.
        combine_documents_chain=combine_documents_chain,
        # If documents exceed context for `StuffDocumentsChain`
        collapse_documents_chain=combine_documents_chain,
        # The maximum number of tokens to group documents into.
        token_max=4000,
    )
    
    map_reduce_chain = MapReduceDocumentsChain(
        # Map chain
        llm_chain=map_chain,
        # Reduce chain
        reduce_documents_chain=reduce_documents_chain,
        # The variable name in the llm_chain to put the documents in
        document_variable_name="docs",
        # Return the results of the map steps in the output
        return_intermediate_steps=False,
    )
    return map_reduce_chain.run(documents)


def get_subject(top_3_feeds):
    # Define prompt
    prompt_template = """Shorten the title below:
    "{text}"
    SHORTENED TITLE:"""
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Define LLM chain
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    
    titles = [title["title"] for title in top_3_feeds]
    shortened_titles = llm_chain.apply(titles)
    
    subject = ""
    for title in shortened_titles[:len(shortened_titles)-1]:
        subject += title + ", "
    subject += shortened_titles[-1]
    return subject