# 🤖 BrainBox : Your Personal Research Assistant

> BrainBox is your all-in-one research assistant that leverages AI to provide comprehensive research support. Discover sources, analyze content, and save notes effortlessly, ensuring you always have relevant information at your fingertips.

## How we built it 🛠️
We built Wiz Search using the following components:
- **LLM:** [Falcon 11b & 180b] for natural language understanding and generation.
- **Embeddings:** [jina-embeddings-v2-base-en](https://jina.ai/embeddings/) to enhance search relevance.
- **Intelligent Search:** [Tavily](https://tavily.com/) for advanced search capabilities.
- **Vector/SQL Databases:** [TiDB](https://www.pingcap.com/tidb/) for efficient data storage and retrieval.
- **Observability:** [Langfuse](https://www.langfuse.com/) for monitoring and observability.
- **UI:** [Streamlit](https://streamlit.io/) for creating an interactive and user-friendly interface.

![flow](./src/assets/get_started.png)

## Run The Application ⚙️
1. Clone the repo
```
git clone https://github.com/SSK-14/BrainBox.ai.git
```

2. Install required libraries

- Create virtual environment
```
pip3 install virtualenv
python3 -m venv {your-venvname}
source {your-venvname}/bin/activate
```

- Install required libraries
```
pip3 install -r requirements.txt
```

- Activate your virtual environment
```
source {your-venvname}/bin/activate
```

3. Set up your `secrets.toml` file
- Copy `example.secrets.toml` into `secrets.toml` and replace the keys

4. Running
```
streamlit run app.py 
```

## Contributing 🤝
Contributions to this project are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request on the project's GitHub repository.

## License 📝
This project is licensed under the [MIT License](https://github.com/SSK-14/BrainBox.ai/blob/main/LICENSE). Feel free to use, modify, and distribute the code as per the terms of the license.
