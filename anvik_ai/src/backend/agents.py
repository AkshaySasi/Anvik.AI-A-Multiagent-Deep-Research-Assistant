import logging
import aiohttp
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.backend.models.research_models import Paper, PaperSummary, ResearchReport
from typing import List, Tuple
from datetime import datetime
import asyncio
import os

class WikipediaFetcher:
    def __init__(self):
        self.logger = logging.getLogger("anvik_ai")
        self.wikipedia_api = WikipediaAPIWrapper()
        self.wikipedia_tool = WikipediaQueryRun(api_wrapper=self.wikipedia_api)
    
    async def fetch_summary(self, topic: str) -> str:
        try:
            self.logger.info(f"Fetching Wikipedia summary for {topic}")
            result = await asyncio.to_thread(self.wikipedia_tool.run, topic)
            if not result:
                self.logger.warning(f"No Wikipedia summary found for {topic}")
                return "No summary available."
            return result
        except Exception as e:
            self.logger.error(f"Error fetching Wikipedia summary: {str(e)}")
            return f"Error fetching Wikipedia summary: {str(e)}"

class ScholarFetcher:
    def __init__(self):
        self.logger = logging.getLogger("anvik_ai")
        self.api_key = os.getenv("SERPAPI_KEY")
        self.base_url = "https://serpapi.com/search"
    
    async def fetch_papers(self, topic: str, max_papers: int = 5) -> List[Paper]:
        try:
            self.logger.info(f"Fetching Google Scholar papers for {topic}")
            params = {
                "engine": "google_scholar",
                "q": topic,
                "api_key": self.api_key,
                "sort": "pubdate",
                "num": max_papers
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        self.logger.error(f"SerpAPI request failed with status {response.status}")
                        return []
                    data = await response.json()
                    papers = []
                    for item in data.get("organic_results", [])[:max_papers]:
                        paper = Paper(
                            title=item.get("title", "Unknown Title"),
                            authors=[a.get("name", "Unknown Author") for a in item.get("publication_info", {}).get("authors", [])],
                            year=int(item.get("publication_info", {}).get("year", datetime.now().year)),
                            abstract=item.get("snippet", "No abstract available"),
                            doi=item.get("resources", [{}])[0].get("file_url", "").split("doi.org/")[-1] if "doi.org" in item.get("resources", [{}])[0].get("file_url", "") else "N/A",
                            url=item.get("link", "N/A")
                        )
                        papers.append(paper)
                    self.logger.info(f"Fetched {len(papers)} papers for {topic}")
                    return papers
        except Exception as e:
            self.logger.error(f"Error fetching Google Scholar papers: {str(e)}")
            return []

class Summarizer:
    def __init__(self):
        self.logger = logging.getLogger("anvik_ai")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY is required but not set")
        self.logger.info(f"Initializing ChatGoogleGenerativeAI with model gemini-2.5-flash")
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key)
        self.summarize_prompt = PromptTemplate(
            input_variables=["abstract", "title"],
            template="Summarize the following abstract in 3-5 sentences, focusing on key findings and methodology. Title: {title}\nAbstract: {abstract}"
        )
    
    async def summarize_papers(self, papers: List[Paper]) -> List[PaperSummary]:
        try:
            self.logger.info(f"Summarizing {len(papers)} papers")
            summaries = []
            for paper in papers:
                summary_chain = self.summarize_prompt | self.llm
                summary = await summary_chain.ainvoke({
                    "title": paper.title,
                    "abstract": paper.abstract
                })
                summaries.append(PaperSummary(
                    title=paper.title,
                    authors=paper.authors,
                    year=paper.year,
                    abstract=paper.abstract,
                    summary=summary.content,
                    doi=paper.doi,
                    url=paper.url
                ))
            self.logger.info("Paper summaries completed")
            return summaries
        except Exception as e:
            self.logger.error(f"Error summarizing papers: {str(e)}")
            return []

class CitationGenerator:
    def __init__(self):
        self.logger = logging.getLogger("anvik_ai")
    
    async def generate_citations(self, paper: PaperSummary) -> Tuple[str, str]:
        try:
            self.logger.info(f"Generating citations for {paper.title}")
            apa = f"{', '.join(paper.authors)}. ({paper.year}). {paper.title}. *Journal Name*. https://doi.org/{paper.doi}"
            mla = f"{', '.join(paper.authors)}. \"{paper.title}.\" *Journal Name*, {paper.year}, doi:{paper.doi}."
            return apa, mla
        except Exception as e:
            self.logger.error(f"Error generating citations: {str(e)}")
            return "Error generating APA citation", "Error generating MLA citation"

class ReportCompiler:
    def __init__(self):
        self.logger = logging.getLogger("anvik_ai")
    
    async def compile_report(self, topic: str, wiki_summary: str, paper_summaries: List[PaperSummary]) -> ResearchReport:
        try:
            self.logger.info(f"Compiling report for {topic}")
            citations_apa = []
            citations_mla = []
            citation_generator = CitationGenerator()
            for paper in paper_summaries:
                apa, mla = await citation_generator.generate_citations(paper)
                citations_apa.append(apa)
                citations_mla.append(mla)
            
            report = ResearchReport(
                topic=topic,
                wikipedia_summary=wiki_summary,
                paper_summaries=paper_summaries,
                citations_apa=citations_apa,
                citations_mla=citations_mla,
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            self.logger.info("Report compilation completed")
            return report
        except Exception as e:
            self.logger.error(f"Error compiling report: {str(e)}")
            return ResearchReport(
                topic=topic,
                wikipedia_summary="Error compiling report",
                paper_summaries=[],
                citations_apa=[],
                citations_mla=[],
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

class Orchestrator:
    def __init__(self):
        self.logger = logging.getLogger("anvik_ai")
        self.wiki_fetcher = WikipediaFetcher()
        self.scholar_fetcher = ScholarFetcher()
        self.summarizer = Summarizer()
        self.report_compiler = ReportCompiler()
    
    async def research_topic(self, topic: str) -> ResearchReport:
        try:
            self.logger.info(f"Starting research pipeline for {topic}")
            
            # Step 1: Fetch Wikipedia summary
            wiki_summary = await self.wiki_fetcher.fetch_summary(topic)
            
            # Step 2: Fetch recent papers
            papers = await self.scholar_fetcher.fetch_papers(topic)
            
            # Step 3: Summarize papers
            paper_summaries = await self.summarizer.summarize_papers(papers)
            
            # Step 4: Compile report
            report = await self.report_compiler.compile_report(topic, wiki_summary, paper_summaries)
            
            return report
        except Exception as e:
            self.logger.error(f"Error in research pipeline: {str(e)}")
            return ResearchReport(
                topic=topic,
                wikipedia_summary="Error in research pipeline",
                paper_summaries=[],
                citations_apa=[],
                citations_mla=[],
                generated_at=""
            )
    
    async def track_research_progress(self, topic: str) -> str:
        try:
            self.logger.info(f"Tracking progress for {topic}")
            return f"Progress on '{topic}': Research completed with Wikipedia summary and paper summaries."
        except Exception as e:
            self.logger.error(f"Error tracking progress: {str(e)}")
            return f"Error tracking progress: {str(e)}"
    
    async def generate_research_proposal(self, topic: str) -> str:
        try:
            self.logger.info(f"Generating research proposal for {topic}")
            proposal = f"Research Proposal: {topic}\n\nObjective: Investigate {topic} through literature review and analysis.\n\nMethodology:\n1. Conduct background research using Wikipedia.\n2. Identify recent papers via Google Scholar.\n3. Summarize findings and compile report.\n\nExpected Outcomes: Comprehensive report with summaries and citations."
            return proposal
        except Exception as e:
            self.logger.error(f"Error generating proposal: {str(e)}")
            return f"Error generating proposal: {str(e)}"