import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import gradio as gr
import aiohttp
import logging
from src.backend.utils.logger import setup_logger

# Set up logging
logger = setup_logger("anvik_ai")

async def research_topic(topic: str, history: list):
    try:
        async with aiohttp.ClientSession() as session:
            # Fetch research
            async with session.post("http://localhost:8000/research", json={"topic": topic}) as response:
                if response.status != 200:
                    logger.error(f"Research API failed with status {response.status}")
                    return history + [{"role": "assistant", "content": f"Error: Research API failed with status {response.status}"}]
                report = await response.json()
            
            # Fetch progress
            async with session.get(f"http://localhost:8000/progress/{topic}") as progress_response:
                if progress_response.status != 200:
                    logger.error(f"Progress API failed with status {progress_response.status}")
                    return history + [{"role": "assistant", "content": f"Error: Progress API failed with status {progress_response.status}"}]
                progress_data = await progress_response.json()
                progress = progress_data["message"]
            
            # Fetch proposal
            async with session.get(f"http://localhost:8000/proposal/{topic}") as proposal_response:
                if proposal_response.status != 200:
                    logger.error(f"Proposal API failed with status {proposal_response.status}")
                    return history + [{"role": "assistant", "content": f"Error: Proposal API failed with status {proposal_response.status}"}]
                proposal_data = await proposal_response.json()
                proposal = proposal_data["proposal"]
            
            # Format response in a conversational style
            response = f"**Research on {report['topic']}**\n\n"
            response += "**Wikipedia Summary**\n"
            response += f"{report['wikipedia_summary']}\n\n"
            
            response += "**Research Papers**\n"
            for paper in report["paper_summaries"]:
                response += (
                    f"**Title**: {paper['title']}\n"
                    f"**Authors**: {', '.join(paper['authors'])}\n"
                    f"**Year**: {paper['year']}\n"
                    f"**Abstract**: {paper['abstract']}\n"
                    f"**Summary**: {paper['summary']}\n"
                    f"**DOI**: {paper['doi']}\n"
                    f"**URL**: [{paper['url']}]({paper['url']})\n\n"
                )
            
            response += "**APA Citations**\n"
            response += "\n".join([f"- {c}" for c in report["citations_apa"]]) + "\n\n"
            
            response += "**MLA Citations**\n"
            response += "\n".join([f"- {c}" for c in report["citations_mla"]]) + "\n\n"
            
            response += "**Progress**\n"
            response += f"{progress}\n\n"
            
            response += "**Research Proposal**\n"
            response += f"{proposal}"
            
            # Append to history
            return history + [
                {"role": "user", "content": topic},
                {"role": "assistant", "content": response}
            ]
    except Exception as e:
        logger.error(f"Error in Gradio interface: {str(e)}")
        return history + [{"role": "assistant", "content": f"Error: {str(e)}"}]

# ChatGPT-like interface
with gr.Blocks(title="Anvik.ai") as demo:
    gr.Markdown("# Hi! I'm Anvik.ai - Your Personal Deep Research Assistant")
    gr.Markdown("Enter a research topic to get a detailed report with Wikipedia summaries, research papers, and citations.")
    chatbot = gr.ChatInterface(
        fn=research_topic,
        chatbot=gr.Chatbot(height=600, type="messages"),
        textbox=gr.Textbox(placeholder="Enter a research topic (e.g., Artificial Intelligence in Healthcare)", container=False),
        title="",
        submit_btn="Research",
        type="messages"
    )

def launch_gradio():
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)

if __name__ == "__main__":
    launch_gradio()