# ⚙️ DOCX to Markdown Processor

![GitHub repo size](https://img.shields.io/github/repo-size/YourUsername/processador-docx?style=flat-square)
![GitHub language count](https://img.shields.io/github/languages/count/YourUsername/processador-docx?style=flat-square)
![GitHub open issues](https://img.shields.io/github/issues/YourUsername/processador-docx?style=flat-square)
![GitHub open pull requests](https://img.shields.io/github/issues-pr/YourUsername/processador-docx?style=flat-square)

This repository contains a Python script designed to automate the conversion of `.docx` files to Markdown format. The tool reads documents from an input folder (`input`), processes their content, and saves the results as `.md` files in an output folder (`output`), preserving the original filenames.

## 📑 Table of Contents

- [Features](#-features)
- [Requirements](#️-requirements)
- [Documentation](#-documentation)
- [Usage Instructions](#-usage-instructions)
- [Acknowledgments](#-acknowledgments)
- [Contact](#-contact)
- [License](#-license)

## ✨ Features

- __Batch Conversion__: Process multiple `.docx` files at once.
- __Simple Structure__: Uses dedicated `input` and `output` folders for easy file management.
- __Text Extraction__: Reads text content from Word documents.
- __Filename Preservation__: Saves converted files with the same name as the original, changing only the extension to `.md`.

## 🛠️ Requirements

- __OS:__ Compatible with Windows, macOS, and Linux.
- __Python:__ Version 3.x.
- __Dependencies:__ All required libraries are listed in the `requirements.txt` file.

## 📚 Documentation
For more details on the main library used for handling DOCX files, refer to the official documentation:

- __python-docx__:
The complete documentation can be found at [python-docx.readthedocs.io](https://python-docx.readthedocs.io/en/latest/). This resource is essential for understanding how text extraction and document manipulation are performed.

## 🚀 Usage Instructions

1. __Clone the Repository__
   ```bash
   git clone https://github.com/YourUsername/processador-docx.git
   cd processador-docx
   ```

2. __Install Dependencies__
   Create and activate a virtual environment, then install the required libraries from the `requirements.txt` file.
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. __Add Your Files__
   Place all the `.docx` files you want to convert into the `input/` folder.

4. __Run the Script__
   Run the main script to start the conversion process.
   ```bash
   python processador.py
   ```

5. __Check the Output__
   The converted Markdown (`.md`) files will be available in the `output/` folder.

## 📝 Acknowledgments

This project was built with the help of several open-source Python libraries, including:
- `python-docx`
- `langchain`
- `deep_translator`

Special thanks to the communities and maintainers of these projects.

## 📞 Contact
For questions or suggestions, feel free to get in touch:
- GitHub: [https://github.com/YourUsername](https://github.com/YourUsername)

## 📜 License
This project is licensed under the MIT License - see the `LICENSE` file for details.