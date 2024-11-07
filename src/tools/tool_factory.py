from langchain_google_community import GmailToolkit
from autogen_ext.tools import LangChainToolAdapter


def get_tools():
    gmailTookit = GmailToolkit()
    tools = gmailTookit.get_tools()

    autogen_tools = [LangChainToolAdapter(tool) for tool in tools]

    return autogen_tools
