import os
import json
import shutil
import sqlalchemy as sqla
from . import db
from server import app
from flask import jsonify
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers.audio import OpenAIWhisperParser, OpenAIWhisperParserLocal
from langchain.document_loaders.blob_loaders.youtube_audio import YoutubeAudioLoader
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate

@app.route(f'/results/<video_id>', methods=['GET','POST'])
def statistics(video_id):
    urls = [f"https://youtu.be/{video_id}"]

    # Testing condition
    # urls = [f"https://youtu.be/jrSwgdiClc0"]

    package_dir = os.path.dirname(__file__)
    sub_dir = "Audio"

    # Directory where the audio will be saved
    save_dir = os.path.join(package_dir, sub_dir)

    loader = GenericLoader(YoutubeAudioLoader(urls, save_dir), OpenAIWhisperParser(api_key="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"))

    docs = loader.load()

    # print(docs)
    # print(docs[0].page_content)

    llm = OpenAI(model_name="gpt-3.5-turbo-16k", openai_api_key="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")

    template = """
    Summarize the following video transcript in one paragraph. Output your summary in json format, with 3 elements: "1_paragraph_summary", "similar_video_idea_summary" (here you should write 5-7 sentences on how a person can record a similar video) and a short (5-7 items) array of video tags/subjects relevant to the vieo idea, named "tags".
    VIDEO: {transcript}
    SUMMARY IN JSON FORMAT:
    """

    prompt_template = PromptTemplate(
        input_variables=["transcript"],
        template=template
    )

    # Transcription of the video
    transcript = docs[0].page_content

    # Sending the prompt to the GPT
    prompt = prompt_template.format(transcript=transcript)

    completion = llm(prompt)
    #Testing condition if everything doesn't work
    # completion = {"1_paragraph_summary":"Suck Chess", "similar_video_idea_summary":"Suck Chess", "tags":["Suck Chess"]}

    # Just writing the response into file so you will not waste money on OpenAI API by sending the requests every time
    # with open("output.txt", "w") as f:
    #     f.write(completion)
    

    completion_dict = json.loads(completion)
    response = jsonify(completion_dict)
    response.headers['Content-Type'] = 'application/json'
    
    shutil.rmtree(save_dir)

    return response

def decode_safely(data):
    if isinstance(data, bytes):
        return data.decode('utf-8', errors='ignore')
    return data


@app.route("/check", methods=['GET'])
def check():
    try:
        # Use the db.session to execute a simple query
        query = sqla.text('SELECT * FROM users')
        result = db.session.execute(query)
        # print(result)
        # Convert the query result to a list
        result_list = []
        for row in result:
            print(row)
            result_list.append(list(row))
        
        db.session.close()
        return jsonify(result_list)
    except Exception as e:
        return str(e)