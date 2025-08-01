from youtube_transcript_api import YouTubeTranscriptApi
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

load_dotenv()

parser = StrOutputParser()
llm = ChatOpenAI(model_name="gpt-4o")

def get_youtube_id(url):
    get_part = url.split("=")[1]
    id = get_part.split("&")[0]
    return id


def get_data(id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(id, languages=['en'])
        data = " ".join(chunk['text'] for chunk in transcript)
        return data
    except Exception as e:
        return None
    

def get_chunks(data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1100, chunk_overlap = 250)
    chunks = text_splitter.create_documents([data])
    return chunks

def get_vector_stores(chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(
    embedding=embeddings,
    documents=chunks 
    )
    return vectorstore

def get_context_document(retriever_docs):
    context_text = "\n\n".join(doc.page_content for doc in retriever_docs)
    return context_text

def generate_answer(question, similarity_retreiver):
    
    answer_prompt = PromptTemplate(
    template="""
    Answer the following question using *only* the information provided in the text below.  
    - Do not use external knowledge or make assumptions.  
    - start your response with phrase "Based on the Video."  
    - If the text does not contain enough information, respond with: "I don't know."
    - Dont ever start with "Generated answer based on the YouTube Transcript:" or any things like this becuase we are showing to our clients 
  

    Question: {question}

    Text: {text}
    """,
        input_variables=["question", "text"]
    )
    
    parallel_chain = RunnableParallel({
    'question' : RunnablePassthrough(),
    'text' : similarity_retreiver | RunnableLambda(get_context_document)
    })
    
    answer_final_chain = parallel_chain | answer_prompt | llm | parser
    
    result = answer_final_chain.invoke(question)
    
    return result

def generate_summary(chunks, max_tokens=4000):
    summary_template = PromptTemplate(
        template="""
        You are a helpful assistant. Summarize the following YouTube transcript content in a clear and concise way.
        Emphasize the key points, use bullet points if needed, and ignore filler content.
        - Dont ever start with "Generated summary of the YouTube Transcript:" or any things like this becuase we are showing to our clients 

        Text:
        {text}
        """,
        input_variables=["text"]
    )

    summary_chain = summary_template | llm | parser
    joined_text = "\n".join(chunk.page_content for chunk in chunks)
    truncated_text = joined_text[:min(len(joined_text), max_tokens * 4)]  # ~4 chars per token

    return summary_chain.invoke({"text": truncated_text})



def generate_note(chunks):
    
    note_template = PromptTemplate(
    template="""
    You are a knowledgeable assistant. Create a well-organized and comprehensive note based on the following text.

    The note should:
    - Cover all important details accurately
    - Include clear headings and subheadings
    - Use bullet points or numbered lists for clarity
    - Incorporate charts or visual explanations where appropriate (describe them if visual rendering isn't possible)
    - Be clean, structured, and easy to understand
    - Dont ever start with "Generated notes of the YouTube Transcript:" or any things like this becuase we are showing to our clients 


    Text:
    {text}
    """,
        input_variables=['text']
    )
    
    note_final_chain = note_template | llm | parser
    
    return note_final_chain.invoke({'text': chunks})


def generate_question(chunks):
    
    question_template = PromptTemplate(
    template="""
    You are an intelligent assistant. Carefully read the following text and generate **10 meaningful questions** that are directly based on its content.

    Guidelines:
    - Each question should be answerable using the information from the text.
    - Focus on key facts, concepts, or important details.
    - Use a mix of question types (e.g., what, why, how, when, who) to ensure variety.
    - Avoid vague or generic questions.
    - Dont ever start with "Generated question of the YouTube Transcript:" or any things like this becuase we are showing to our clients 

    Text:
    {text}
    """,
        input_variables=['text']
    )
    
    question_final_chain = question_template | llm | parser

    return question_final_chain.invoke({'text': chunks})
