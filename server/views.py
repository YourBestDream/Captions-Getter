import os
import json
import shutil
import g4f
import sqlalchemy as sqla
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, String, DateTime, MetaData, JSON, text, select
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from . import db
from dotenv import load_dotenv
from server import app
from flask import jsonify
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers.audio import OpenAIWhisperParser, OpenAIWhisperParserLocal
from langchain.document_loaders.blob_loaders.youtube_audio import YoutubeAudioLoader
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate

load_dotenv()


@app.route("/retrieve/<user_id>", methods=['GET', 'POST'])
def retrieve(user_id):
    try:
        query = text('''
            SELECT v.video_id, v.video_name 
            FROM user_videos uv
            JOIN videos v ON uv.video_id = v.video_id
            WHERE uv.user_id = :user_id;
        ''')

        result = db.session.execute(query, {"user_id": user_id})

        videos_info = []
        for row in result:
            video_data = {
                "video_id": row.video_id,
                "video_name": row.video_name
            }
            videos_info.append(video_data)

        db.session.close()
        return jsonify(videos_info)

    except Exception as e:
        return str(e)


@app.route(f'/results/<video_id>', methods=['GET','POST'])
def statistics(video_id):
    try:
        # Create a SQL query to check for the existence of the video_id
        query = text("SELECT COUNT(*) FROM videos WHERE video_id = :video_id")
        result = db.session.execute(query, {"video_id": video_id})

        count = result.scalar()

        db.session.close()

        if count > 0:
            # If the video_id already exists in the database, return the result
            query = text("SELECT summary, possible_idea, possible_tags FROM videos WHERE video_id = :video_id")
            result = db.session.execute(query, {"video_id": video_id})

            # Convert the query result to a list of dictionaries
            result_list = []
            for row in result:
                result_dict = {
                    "1_paragraph_summary": row[0],
                    "similar_video_idea_summary": row[1],
                    "tags": row[2]
                }
                

            db.session.close()
            return jsonify(result_dict)
        else:
            urls = [f"https://youtu.be/{video_id}"]

            # Testing condition
            # urls = [f"https://youtu.be/jrSwgdiClc0"]

            package_dir = os.path.dirname(__file__)
            sub_dir = "Audio"

            # Directory where the audio will be saved
            save_dir = os.path.join(package_dir, sub_dir)


            loader = GenericLoader(YoutubeAudioLoader(urls, save_dir), OpenAIWhisperParser(api_key=os.getenv("API_KEY")))


            docs = loader.load()
            audio_files = os.listdir(save_dir)
            video_name_fr = None
            for file in audio_files:
                # If you need to match the file with a specific video_id, you might need additional logic here
                video_name_fr = os.path.basename(file).split('.')[0]
                break

            # print(docs)
            # print(docs[0].page_content)

            # llm = OpenAI(model_name="gpt-3.5-turbo-16k", openai_api_key=os.getenv("API_KEY"))

            transcript = docs[0].page_content

            response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_35_turbo_16k,
            messages=[{"role": "user", "content": f'''
                        Summarize the following video transcript in one paragraph. Output your summary in json format, with 3 elements: "1_paragraph_summary", "similar_video_idea_summary" (here you should write 5-7 sentences on how a person can record a similar video) and a short (5-7 items) array of video tags/subjects relevant to the vieo idea, named "tags".
                        VIDEO: {transcript}
                        SUMMARY IN JSON FORMAT:
            '''
            }],
            )
            # prompt_template = PromptTemplate(
            #     input_variables=["transcript"],
            #     template=template
            # )

            # Transcription of the video
            
            # Sending the prompt to the GPT
            # prompt = prompt_template.format(transcript=transcript)

            completion = response
            # Testing condition if everything doesn't work
            # completion = {"1_paragraph_summary":"Suck Chess", "similar_video_idea_summary":"Suck Chess", "tags":["Suck Chess"]}

            # Just writing the response into file so you will not waste money on OpenAI API by sending the requests every time
            # with open("output.txt", "w") as f:
            #     f.write(completion)


            completion_dict = json.loads(completion)
            print(completion_dict)
            response = jsonify(completion_dict)
            print(response)
            response.headers['Content-Type'] = 'application/json'
            
            try:
                one_paragraph_summary = completion_dict["1_paragraph_summary"]
                similar_video_idea_summary = completion_dict["similar_video_idea_summary"]
                tags = completion_dict["tags"]  # Tags are already in the correct format

                # Preparing the data for insertion
                data_to_insert = {
                    "id": str(uuid4()),  # Generating a new UUID
                    "video_id": video_id,
                    "summary": one_paragraph_summary,
                    "possible_idea": similar_video_idea_summary,
                    "tags": None,
                    "possible_tags": json.dumps(tags),  # Convert the list to a JSON formatted string
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "video_name":video_name_fr
                }

                # Insert data into the PostgreSQL table
                sql = text("""
                    INSERT INTO videos (id, video_id, summary, possible_idea, tags, possible_tags, created_at, updated_at, video_name)
                    VALUES (:id, :video_id, :summary, :possible_idea, :tags, :possible_tags, :created_at, :updated_at, :video_name)
                """)

                db.session.execute(sql, data_to_insert)
                db.session.commit()

            except Exception as e:
                # Handle any exceptions that arise
                print(f"Error while inserting into the database: {e}")

            shutil.rmtree(save_dir)

            return response
    except Exception as e:
        return str(e)

def decode_safely(data):
    if isinstance(data, bytes):
        return data.decode('utf-8', errors='ignore')
    return data

@app.route("/table", methods=['GET'])
def table_structure():
    try:
        # Use the db.session to execute a query to get the column names and data types
        query = sqla.text('''
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'videos'
        ''')
        result = db.session.execute(query)

        # Convert the query result to a dictionary
        columns = {}
        for row in result:
            columns[row.column_name] = row.data_type

        db.session.close()
        return jsonify(columns)
    except Exception as e:
        return str(e)


@app.route("/check", methods=['GET'])
def check():
    try:
        # Use the db.session to execute a simple query
        query = text('ALTER TABLE "videos" ALTER COLUMN summary TYPE VARCHAR(4000)')
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