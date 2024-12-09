# 🌟 Welcome to Aura - My Personal AI Assistant Journey! 

Hey there! 👋 Welcome to my open-source project where I'm documenting my journey of creating Aura, my personal AI assistant. This project represents my exploration into building an AI companion that helps me with everyday developer tasks.

## 🎯 Vision
Starting with simple email management tasks, Aura is designed to grow and evolve, continuously expanding its capabilities to become a more comprehensive developer assistant. This is just the beginning of an exciting journey where I'll be pushing the boundaries of what's possible with AI assistance in development workflows.

## 📚 Follow Along
I'm sharing my experiences, challenges, and learnings through a series of blog posts on Medium. If you're interested in the behind-the-scenes of building an AI assistant, or want to learn from my experiences, check out my articles:

[Follow my journey on Medium](https://medium.com/@richard.gyiko)

## ✨ Features

### How to Use
Aura is currently a console-based application where you can interact with it through simple text commands. Just run the application and start typing your requests - Aura will help you manage your emails through natural language interactions! Don't expect too much just yet, we're just getting started... 😉

### Planned Capabilities
- [x] Tools: Gmail - Get and search emails
- [x] Tools: Gmail - Create draft emails
- [x] Tools: Google Calendar - Get and search events
- [x] Tools: Google Calendar - Create events
- [ ] Tools: Playwright - Automate web interactions
- [ ] Tools: Notion - Create and manage notes, datasets, and tasks
- [ ] Tools: File System - Manage files and directories
- [ ] Tools: GitHub - Manage issues for project management
- [ ] Agent: Inbox Assistant
  - [ ] Extra: Unsubscribe from newsletters
  - [ ] Extra: Download attachments for further processing
- [ ] Agent: Schedule Coordinator
- [ ] Agent: Research Assistant
- [ ] Agent: Project Management Assistant
- [ ] Team Collaboration: Organize agents to teams for specific tasks
- [ ] Personalization: Learn from user interactions (Mem0)
- [ ] Personalization: Introduce voice interactions
- [ ] Agent: Coding Assistant (Integrating Aider somehow?)


## 🚀 Getting Started
To run Aura on your local machine, follow these steps:

### Prerequisites
- Python 3.12 or higher
- A Google Cloud Platform project with the Gmail API and Google Calendar API enabled
- A Google Cloud Platform service account with the necessary permissions
- A `credentials.json` file for the service account placed in the root directory
- A `.env` file with the following environment variables:
  - `OPENAI_API_KEY` - Your OpenAI API key
  - `OPENAI_ORG_ID` - Your OpenAI organization ID (optional)
  - `OPENAI_PROJECT_ID` - Your OpenAI project ID (optional)

### Running the Application

```bash
python -m src.main
```

### Running Tests
  
```bash
python -m unittest src/tests/test_lancedb_integration.py -v
```

### Technical ToDos
- [ ] Upgrade to the AgentChat layer if mature enough

## 🤝 Join the Journey
This is an open-source project, and I believe in the power of community and shared knowledge. Feel free to explore the code, share your thoughts, or even contribute to Aura's development!

Stay tuned for more updates as Aura grows and evolves! ✨
