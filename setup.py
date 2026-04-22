from setuptools import setup, find_packages

setup(
    name="finance_agent_rag",
    version="0.2.0",
    packages=find_packages(include=["finance_agent_rag", "finance_agent_rag.*"]),
)
