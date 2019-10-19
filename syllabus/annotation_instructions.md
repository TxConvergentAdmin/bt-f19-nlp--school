# Using cdQA-annotator:

First, we need to install the necessary packages.

```shell
pip3 install cdQA-annotator
```

And then import them:

```shell
from cdqa.utils.converters import df2squad
from cdqa.utils.converters import pdf_converter
```

Now, create a folder holding your syllabus pdf files on your computer.
We're going to convert these pdf files to a format that the annotator will
accept in a couple of steps. Use the line below, filling in the
filepath to your syllabus file directory.
(For Ubuntu, just add '/mnt/c' to the beginning of the directory path.)

```shell
df = pdf_converter(directory_path='PATH_TO_PDFS_DIRECTORY')
```

Next, we'll save this data as a JSON file in the SQUAD format, which can
be uploaded to the annotator.

```shell
json_data = df2squad(df=df, squad_version='v1.1', output_dir='PATH_TO_OUTPUT_JSON', filename='FILENAME.json')
```

Then we go to a shell prompt for these steps:
Clone the repository:

```shell
git clone https://github.com/cdqa-suite/cdQA-annotator
```

Install dependencies

```shell
cd cdQA-annotator
npm install
```

Start development server

```shell
cd src
npm run serve
```

The app should be running at http://localhost:8080/, type this link into any browser
and the annotating app should be running. From there, use the cdQA-annotator section
in this article:
https://towardsdatascience.com/how-to-create-your-own-question-answering-system-easily-with-python-2ef8abc8eb5
